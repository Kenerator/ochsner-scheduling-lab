"""Bounded Responses extraction adapter. It cannot authorize scheduling effects."""
import json
import math
import os
from time import monotonic
from urllib.request import Request, urlopen
from .interpretation import (FIELD_NAMES, INTENTS, INTERPRETATION_SCHEMA,
                             InterpretationError, validate_action)

_INSTRUCTIONS = '''Extract scheduling intent, nullable field patches and displayed option ordinal only.
Never invent service facts, identifiers or consent. Null means unchanged. Use current intent
for answers to follow-up questions. Whole-message yes/confirm is unclear with no patches;
local deterministic code owns consent. Medical questions are medical_advice; unsupported
specialties/services are unsupported. Dates must be ISO calendar dates. Return schema JSON.'''


def _unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise ValueError('Duplicate JSON key')
        result[key]=value
    return result


def _context(context):
    """Project only nonidentity facts; never forward caller's session dictionary."""
    intent=context.get('intent','unclear')
    if intent not in INTENTS: intent='unclear'
    present=context.get('fields_present',[])
    if not isinstance(present,(list,tuple,set)): present=[]
    present=[name for name in FIELD_NAMES if name in present]
    count=context.get('slot_count',0)
    if type(count) is not int or not 0 <= count <= 100: count=0
    return {'intent':intent,'fields_present':present,'slot_count':count}

class OpenAIInterpreter:
    def __init__(self, model='gpt-5.4-mini', key=None, events=None, timeout=30, opener=None):
        self.model=os.environ.get('OPENAI_MODEL',model) if model=='gpt-5.4-mini' else model
        self.key=os.environ.get('OPENAI_API_KEY') if key is None else key
        self.events=events
        if not isinstance(timeout,(int,float)) or isinstance(timeout,bool) or not math.isfinite(timeout) or not 0 < timeout <= 120:
            raise InterpretationError('Invalid model timeout')
        self.timeout=timeout
        self.opener=opener or urlopen

    def interpret(self,text,context):
        started=monotonic()
        try:
            if not self.key: raise InterpretationError('Set OPENAI_API_KEY for live interpretation')
            if not isinstance(text,str) or not text.strip() or len(text)>8000: raise ValueError()
            if not isinstance(context,dict): raise ValueError()
            safe_context=_context(context)
            body={
                'model':self.model,'store':False,'max_output_tokens':500,
                'instructions':_INSTRUCTIONS,
                'input':json.dumps({'text':text,'context':safe_context}),
                'text':{'format':{'type':'json_schema','name':'appointment_interpretation',
                                  'strict':True,'schema':INTERPRETATION_SCHEMA}},
            }
            request=Request('https://api.openai.com/v1/responses',data=json.dumps(body).encode(),
                            headers={'Authorization':'Bearer '+self.key,'Content-Type':'application/json'},method='POST')
            with self.opener(request,timeout=self.timeout) as response:
                raw=response.read(262145)
            if len(raw)>262144: raise ValueError()
            result=json.loads(raw,object_pairs_hook=_unique_object)
            if not isinstance(result,dict) or result.get('status')!='completed': raise ValueError()
            outputs=[]
            for item in result.get('output',[]):
                if not isinstance(item,dict): raise ValueError()
                if item.get('type')=='message':
                    if item.get('role')!='assistant': raise ValueError()
                    for content in item.get('content',[]):
                        if not isinstance(content,dict) or content.get('type')!='output_text': raise ValueError()
                        outputs.append(content.get('text'))
            if len(outputs)!=1 or not isinstance(outputs[0],str): raise ValueError()
            action=validate_action(json.loads(outputs[0],object_pairs_hook=_unique_object))
            # Session checks current choices; schema-valid ordinals are not consent.
            if self.events is not None:
                self.events.emit('interpretation',intent=action.intent,outcome='completed',elapsed_ms=round((monotonic()-started)*1000,3))
            return action
        except Exception:
            if self.events is not None:
                self.events.emit('interpretation',outcome='failed',reason='model_unavailable',elapsed_ms=round((monotonic()-started)*1000,3))
            message='Set OPENAI_API_KEY for live interpretation' if not self.key else 'Model interpretation unavailable; try again or request human assistance'
            raise InterpretationError(message) from None
