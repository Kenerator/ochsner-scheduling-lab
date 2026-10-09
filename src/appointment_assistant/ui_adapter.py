"""Thin explicit-chat submission boundary; reading evidence never advances a session."""
from threading import RLock

class ChatAdapter:
    def __init__(self,session):
        self.session=session
        self._receipts={}
        self._lock=RLock()

    def respond(self,messages,config=None):
        """One user message adds one generation; reactive reentry reuses its receipt.

        Marimo calls this only for submitted chat messages. Editing an existing
        history does not create a generation or replace its reserved outcome.
        Config is intentionally unused: it cannot grant effects or choose keys.
        """
        users=[message for message in messages if getattr(message,'role',None)=='user']
        if not users: return 'Enter a scheduling request to begin.'
        generation=len(users)
        with self._lock:
            if generation in self._receipts: return self._receipts[generation]
            text=getattr(users[-1],'content',None)
            if not isinstance(text,str): return 'Enter a text scheduling request.'
            self._receipts[generation]='This submission is processing. Please wait for its outcome.'
            try:
                result=self.session.submit(text,generation)
                if isinstance(getattr(result,'message',None),str):
                    message=result.message
                elif getattr(result,'status',None)=='in_progress':
                    message='This submission is processing. Please wait for its outcome.'
                else:
                    message='The submission could not complete. Its effects may be unknown; contact scheduling staff before retrying.'
            except Exception:
                # An exception after dispatch cannot establish that nothing happened.
                message='The submission could not complete. Its effects may be unknown; contact scheduling staff before retrying.'
            self._receipts[generation]=message
            return message

    def evidence(self):
        return self.session.events.snapshot()


class FormAdapter:
    """Explicit form callbacks assign generations; render methods are read-only."""
    def __init__(self,session):
        self.session=session
        self._chat=ChatAdapter(session)
        self._messages=[]
        self._transcript=[]
        self._lock=RLock()

    def submit(self,text):
        if text is None: return
        if not isinstance(text,str): return
        from types import SimpleNamespace
        with self._lock:
            # Append before dispatch: even a failed attempt consumes its generation.
            self._messages.append(SimpleNamespace(role='user',content=text))
            reply=self._chat.respond(self._messages)
            self._transcript.append((text,reply))
            return reply

    def transcript(self):
        with self._lock:
            return self._transcript.copy()

    def evidence(self):
        return self.session.events.snapshot()


def create_session(mode,api_base,model,scenario=None):
    """Create the same deterministic core as CLI; live credentials stay in env."""
    from .conversation import Session
    from .events import Evidence
    from .interpretation import RehearsalInterpreter
    from .openai_interpreter import OpenAIInterpreter
    from .scheduling import SchedulingAPI
    if mode not in ('openai','rehearsal'): raise ValueError('SCHEDULING_MODE must be openai or rehearsal')
    events=Evidence()
    api=SchedulingAPI(api_base,events=events,scenario=scenario)
    interpreter=OpenAIInterpreter(model=model,events=events) if mode=='openai' else RehearsalInterpreter()
    return Session(api,interpreter,events=events)
