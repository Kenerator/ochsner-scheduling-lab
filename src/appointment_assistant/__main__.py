"""Thin CLI and isolated supplied-mock demonstrations."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
from threading import Thread
from http.server import ThreadingHTTPServer
from time import monotonic
from .conversation import Session, TurnResult
from .events import Evidence
from .interpretation import RehearsalInterpreter, InterpretationError
from .openai_interpreter import OpenAIInterpreter
from .scheduling import SchedulingAPI

DEMOS={
 'provider_lookup':['Which primary care providers are downtown?'],
 'happy_path_booking':['I want to book a primary care appointment downtown.','My phone is 555-0101.','My date of birth is 1985-04-12.','1','yes'],
 'no_patient_match':['I want to book primary care.','555-9999','1990-01-01','I want a human'],
 'multiple_patient_matches':['Book primary care downtown.','555-0130','1978-09-22','My ZIP code is 70115','1','yes'],
 'appointment_lookup':['Look up my appointments.','555-0101','1985-04-12'],
 'slot_conflict':['Book primary care downtown.','555-0101','1985-04-12','__conflict_choice__','yes'],
 'handoff':['I want to speak to a human scheduling representative.'],
 'api_failure':['Which primary care providers are downtown?'],
}

def create_session(mode='openai',api_base='http://127.0.0.1:4013',model='gpt-5.4-mini',scenario=None):
    events=Evidence()
    interpreter=OpenAIInterpreter(model=model,events=events) if mode=='openai' else RehearsalInterpreter()
    api=SchedulingAPI(api_base,events=events,scenario=scenario)
    return Session(api,interpreter,events=events)

def _reference():
    """Run unchanged supplied routes/store; suppress upstream raw audit in demos."""
    root=Path(__file__).resolve().parents[2]
    spec=importlib.util.spec_from_file_location('supplied_reference',root/'vendor/reference-api/mock-api/server.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    class Handler(module.Handler):
        store=module.Store()
        def audit(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    return server,thread

def run_demo(name,mode,model,scenario=None,json_summary=False):
    server,thread=_reference();started=monotonic()
    try:
        session=create_session(mode,'http://127.0.0.1:'+str(server.server_port),model,scenario or ('api_failure' if name=='api_failure' else None))
        results=[]
        for text in DEMOS[name]:
            if text=='__conflict_choice__':
                text=str(next(i+1 for i,s in enumerate(session.slots) if s['slotId']=='slot_conflict_001'))
            result=session.submit(text);results.append(result)
            if not json_summary:print(result.message)
        summary={'scenario':name,'mode':mode,'model':model if mode=='openai' else None,
                 'isolated_reference':True,'states':[r.state for r in results],
                 'outcome':results[-1].outcome,'duration_ms':round((monotonic()-started)*1000,1),
                 'events':session.events.snapshot()}
        if json_summary:print(json.dumps(summary))
        return summary
    finally:
        server.shutdown();server.server_close();thread.join(2)

def main(argv=None):
    p=argparse.ArgumentParser(description='Synthetic scheduling AI Lab; no medical advice.')
    p.add_argument('--mode',choices=['openai','rehearsal'],default=os.environ.get('SCHEDULING_MODE','openai'))
    p.add_argument('--api-base',default=os.environ.get('API_BASE','http://127.0.0.1:4013'))
    p.add_argument('--model',default=os.environ.get('OPENAI_MODEL','gpt-5.4-mini'))
    p.add_argument('--mock-scenario',choices=['api_failure'])
    p.add_argument('--demo',choices=list(DEMOS))
    p.add_argument('--scenario',choices=['success','failure'],help='aliases for required happy/no-match demonstrations')
    p.add_argument('--json-summary',action='store_true',help='redacted metadata only; no transcript or identity')
    args=p.parse_args(argv)
    if args.mode=='openai' and not os.environ.get('OPENAI_API_KEY'):
        print('Live mode requires OPENAI_API_KEY in the process environment. Set it securely or explicitly choose --mode rehearsal for deterministic simulation.',file=sys.stderr);return 2
    demo=args.demo or ({'success':'happy_path_booking','failure':'no_patient_match'}.get(args.scenario))
    try:
        if demo:
            run_demo(demo,args.mode,args.model,args.mock_scenario,args.json_summary);return 0
        session=create_session(args.mode,args.api_base,args.model,args.mock_scenario)
        print('AI Scheduling Lab — '+('LIVE OpenAI interpretation' if args.mode=='openai' else 'DETERMINISTIC REHEARSAL; no live AI')+'. Synthetic data only. No medical advice.')
        print('Type exit to end. Reset clears conversation only; unknown writes need human reconciliation.')
        while True:
            try:text=input('You: ')
            except EOFError:break
            if text.strip().casefold() in ('exit','quit'):break
            out=session.submit(text)
            print('Assistant: '+getattr(out,'message','Submission is '+getattr(out,'status','unavailable')+'.'))
        return 0
    except (InterpretationError,ValueError):
        print('The interpreter or configuration is unavailable. Check process environment and model; no automatic fallback was used.',file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
