"""Responses-shaped injected doubles through real Session and supplied mock.

These tests demonstrate integration contracts, never live OpenAI access.
"""
import io
import json
import unittest
from appointment_assistant.conversation import Session
from appointment_assistant.events import Evidence
from appointment_assistant.interpretation import FIELD_NAMES
from appointment_assistant.openai_interpreter import OpenAIInterpreter
from appointment_assistant.scheduling import SchedulingAPI
from helpers import reference_server


def action(intent='unclear', ordinal=None, **fields):
    return dict(intent=intent,fields=dict(dict.fromkeys(FIELD_NAMES), **fields),option_ordinal=ordinal)

def envelope(proposal):
    return {'status':'completed','output':[{'type':'message','role':'assistant','content':[{'type':'output_text','text':json.dumps(proposal)}]}]}

class ResponsesDouble:
    def __init__(self, responses):
        self.responses=iter(responses)
        self.requests=[]
    def __call__(self, request, timeout):
        self.requests.append(json.loads(request.data))
        return io.BytesIO(json.dumps(next(self.responses)).encode())

class LiveConversationIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.server,self.thread,self.store=reference_server()
        self.events=Evidence()
        self.api=SchedulingAPI('http://127.0.0.1:'+str(self.server.server_port),events=self.events)
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join()
    def session(self, proposals):
        self.double=ResponsesDouble([envelope(p) for p in proposals])
        return Session(self.api,OpenAIInterpreter(key='synthetic-double-only',opener=self.double,events=self.events),events=self.events)

    def test_provider_multi_turn_uses_responses_extraction_and_actual_records(self):
        session=self.session([action('provider_lookup',location='downtown'),action('provider_lookup',specialty='primary_care')])
        first=session.submit('Find providers downtown')
        self.assertEqual(first.state,'clarify')
        self.assertFalse(any(e['category']=='api' for e in self.events.snapshot()))
        second=session.submit('Primary care please')
        self.assertEqual(second.state,'providers')
        self.assertIn('Dr. Elena Brooks',second.message)
        self.assertIn('Dr. Marcus King',second.message)
        self.assertNotIn('Dr. Priya Shah',second.message)
        self.assertEqual(len(self.double.requests),2)
        context=json.loads(self.double.requests[1]['input'])['context']
        self.assertEqual(context['intent'],'provider_lookup')
        self.assertIn('location',context['fields_present'])
        self.assertEqual(len(self.store.appointments),2)
        self.assertFalse(self.store.handoffs)

    def test_booking_multi_turn_literal_consent_after_returned_selection(self):
        session=self.session([action('book',specialty='primary_care',location='downtown'),action('book',phone='555-0101'),action('book',dob='1985-04-12'),action('book',ordinal=1),action()])
        outputs=[]
        for text in ('Book primary care downtown','My phone is 555-0101','Born 1985-04-12','The first option'):
            outputs.append(session.submit(text))
            self.assertEqual(len(self.store.appointments),2)
        self.assertEqual(outputs[-2].state,'slots')
        self.assertIn('-05:00',outputs[-2].message)
        self.assertEqual(outputs[-1].state,'proposal')
        selected=dict(session.proposal['slot'])
        final=session.submit('yes')
        self.assertEqual(final.state,'booked')
        self.assertEqual(final.outcome,'completed')
        self.assertEqual(len(self.store.appointments),3)
        record=self.api.appointments('pat_1001')[-1]
        for key in ('providerId','specialty','location','startTime'): self.assertEqual(record[key],selected[key])
        projected=json.loads(self.double.requests[-1]['input'])['context']
        self.assertNotIn('pat_1001',json.dumps(projected))
        self.assertNotIn('555-0101',json.dumps(projected))
        self.assertNotIn('synthetic-double-only',json.dumps(self.events.snapshot()))

    def test_no_match_multi_turn_has_no_patient_specific_effect(self):
        session=self.session([action('book',specialty='primary_care'),action('book',phone='555-9999'),action('book',dob='1990-01-01'),action('human_request')])
        for text in ('Book primary care','555-9999','1990-01-01'):
            result=session.submit(text)
        self.assertIn('No patient match',result.message)
        self.assertIsNone(session.patient)
        self.assertEqual(len(self.store.appointments),2)
        self.assertFalse(any(e.get('route') in ('/availability','/appointments') for e in self.events.snapshot()))
        final=session.submit('A human please')
        self.assertEqual(final.state,'handoff')
        self.assertEqual(final.outcome,'completed')
        self.assertIsNone(self.store.handoffs[0]['patientId'])
        self.assertNotIn('555-9999',self.store.handoffs[0]['summary'])

    def test_invalid_and_refused_extraction_never_call_scheduling(self):
        refusal={'status':'completed','output':[{'type':'message','role':'assistant','content':[{'type':'refusal','refusal':'PRIVATE CANARY'}]}]}
        for response in (envelope(action('book',ordinal=True)),envelope(dict(action('book'),confirmed=True)),refusal,{'status':'incomplete','output':[]}):
            with self.subTest(response=response):
                self.events=Evidence()
                double=ResponsesDouble([response])
                session=Session(SchedulingAPI('http://127.0.0.1:'+str(self.server.server_port),events=self.events),OpenAIInterpreter(key='double',opener=double,events=self.events),events=self.events)
                result=session.submit('Please book')
                self.assertEqual(result.state,'blocked')
                self.assertEqual(result.outcome,'rejected')
                self.assertFalse(any(e['category']=='api' for e in self.events.snapshot()))
                self.assertEqual(len(self.store.appointments),2)
                self.assertFalse(self.store.handoffs)
                self.assertNotIn('PRIVATE CANARY',result.message+json.dumps(self.events.snapshot()))

if __name__=='__main__': unittest.main()
