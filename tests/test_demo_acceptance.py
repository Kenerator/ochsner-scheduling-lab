"""All reviewer CLI demos are isolated supplied-mock rehearsals, never live proof."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from appointment_assistant.conversation import Session
from appointment_assistant.interpretation import RehearsalInterpreter
from appointment_assistant.scheduling import SchedulingAPI, SchedulingError
from helpers import reference_server

ROOT=Path(__file__).resolve().parents[1]

class DemoAcceptanceTests(unittest.TestCase):
    def run_demo(self,name):
        env={**os.environ,'PYTHONPATH':str(ROOT/'src')}
        env.pop('OPENAI_API_KEY',None)
        run=subprocess.run([sys.executable,'-m','appointment_assistant','--mode','rehearsal','--demo',name,'--json-summary'],cwd=ROOT,env=env,capture_output=True,text=True,timeout=40)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertEqual(run.stderr,'')
        result=json.loads(run.stdout)
        self.assertEqual(result['mode'],'rehearsal')
        self.assertIsNone(result['model'])
        self.assertTrue(result['isolated_reference'])
        for private in ('555-','1985-04-12','pat_1001','pat_1003','70115','/RFP/','OPENAI_API_KEY'):
            self.assertNotIn(private,run.stdout)
        return result

    def test_all_eight_demos_have_expected_terminal_state_and_private_effects(self):
        cases={'provider_lookup':('providers','not_attempted',0,0),
               'happy_path_booking':('booked','completed',1,0),
               'no_patient_match':('handoff','completed',0,1),
               'multiple_patient_matches':('booked','completed',1,0),
               'appointment_lookup':('appointments','not_attempted',0,0),
               'slot_conflict':('conflict','rejected',1,0),
               'handoff':('handoff','completed',0,1),
               'api_failure':('handoff','rejected',0,1)}
        for name,(state,outcome,book_count,handoff_count) in cases.items():
            with self.subTest(name=name):
                result=self.run_demo(name)
                self.assertEqual(result['scenario'],name)
                self.assertEqual(result['states'][-1],state)
                self.assertEqual(result['outcome'],outcome)
                api=[e for e in result['events'] if e['category']=='api']
                self.assertEqual(sum(e['route']=='/appointments' and e['method']=='POST' for e in api),book_count)
                self.assertEqual(sum(e['route']=='/handoffs' and e['method']=='POST' for e in api),handoff_count)
                if name=='api_failure':
                    self.assertTrue(all(e['status']==503 and e['outcome']=='rejected' for e in api))
                if name=='slot_conflict':
                    self.assertTrue(any(e.get('status')==409 for e in api))

    def test_repeated_booking_demo_restarts_private_fixture_store(self):
        first=self.run_demo('happy_path_booking')
        second=self.run_demo('happy_path_booking')
        self.assertEqual(first['states'],second['states'])
        self.assertEqual(second['states'][-1],'booked')
        for result in (first,second):
            writes=[e for e in result['events'] if e['category']=='api' and e.get('route')=='/appointments']
            self.assertEqual(len(writes),1)
            self.assertEqual(writes[0]['status'],201)

    def test_session_reset_preserves_bookings_and_unknown_reset_requires_reconciliation(self):
        server,thread,store=reference_server()
        try:
            api=SchedulingAPI('http://127.0.0.1:'+str(server.server_port))
            session=Session(api,RehearsalInterpreter())
            for text in ('Book primary care downtown','555-0101','1985-04-12','1','yes'): result=session.submit(text)
            self.assertEqual(result.state,'booked')
            result=session.submit('reset')
            self.assertEqual(result.state,'start')
            self.assertEqual(len(store.appointments),3)
            self.assertIsNone(session.patient)
            self.assertIsNone(session.proposal)
            self.assertIn('bookings remain',result.message)
            unknown=Session(api,RehearsalInterpreter())
            for text in ('Book primary care downtown','555-0101','1985-04-12','1'): unknown.submit(text)
            def lost(*args,**kwargs): raise SchedulingError('unknown',unknown=True)
            api.book=lost
            result=unknown.submit('yes')
            self.assertEqual(result.outcome,'unknown')
            result=unknown.submit('reset')
            self.assertEqual(result.state,'blocked')
            self.assertEqual(result.outcome,'unknown')
            self.assertIn('reconcile',result.message)
            self.assertEqual(len(store.appointments),3)
        finally:
            server.shutdown();server.server_close();thread.join()

if __name__=='__main__': unittest.main()
