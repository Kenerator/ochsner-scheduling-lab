"""Responses-shaped external doubles; these do not qualify live model access."""
import io
import json
import unittest
from appointment_assistant.openai_interpreter import OpenAIInterpreter
from appointment_assistant.interpretation import InterpretationError

FIELDS=dict.fromkeys(("phone","dob","zip_code","start_date","end_date","specialty","location"))
def response(action=None):
    return {"status":"completed","output":[{"type":"message","role":"assistant","content":[{"type":"output_text","text":json.dumps(action or {"intent":"book","fields":FIELDS,"option_ordinal":None})}]}]}
class Events:
    def __init__(self): self.rows=[]
    def emit(self,category,**fields): self.rows.append({"category":category,**fields})
class LiveBoundaryTests(unittest.TestCase):
    def test_request_strict_schema_private_context_and_finite_bounds(self):
        captured=[]
        def opener(request,timeout):
            captured.append((request,timeout)); return io.BytesIO(json.dumps(response()).encode())
        events=Events()
        result=OpenAIInterpreter(key="secret-canary",opener=opener,events=events).interpret("Book care",{"intent":"book","fields_present":["phone"],"slot_count":2,"patientId":"identity-canary","candidates":["candidate-canary"]})
        self.assertEqual(result.intent,"book")
        request,timeout=captured[0]
        body=json.loads(request.data)
        self.assertFalse(body["store"])
        self.assertTrue(body["text"]["format"]["strict"])
        self.assertGreater(body["max_output_tokens"],0)
        self.assertGreater(timeout,0)
        self.assertNotIn("identity-canary",request.data.decode())
        self.assertNotIn("candidate-canary",request.data.decode())
        self.assertEqual(events.rows[0]["outcome"],"completed")
        self.assertNotIn("secret-canary",json.dumps(events.rows))

    def test_refusal_incomplete_duplicate_missing_and_invalid_output_fail_closed(self):
        bodies=[response(),response(),response(),response(),response({"intent":"book","fields":FIELDS,"option_ordinal":True})]
        bodies[0]["status"]="incomplete"
        bodies[1]["output"][0]["content"]=[{"type":"refusal","refusal":"private-canary"}]
        bodies[2]["output"]*=2
        bodies[3]["output"]=[]
        for body in bodies:
            with self.subTest(body=body), self.assertRaises(InterpretationError):
                OpenAIInterpreter(key="k",opener=lambda *a,**k:io.BytesIO(json.dumps(body).encode())).interpret("hello",{})

    def test_exception_sanitized_no_retry_or_rehearsal(self):
        count=[]; events=Events()
        def unavailable(*args,**kwargs): count.append(1); raise OSError("private-canary")
        with self.assertRaises(InterpretationError) as caught:
            OpenAIInterpreter(key="k",opener=unavailable,events=events).interpret("private-utterance",{})
        self.assertEqual(len(count),1)
        self.assertNotIn("private",str(caught.exception))
        self.assertNotIn("private",json.dumps(events.rows))
        self.assertEqual(events.rows[0]["reason"],"model_unavailable")

    def test_ordinal_outside_display_and_oversized_text_fail_closed(self):
        body=response({"intent":"book","fields":FIELDS,"option_ordinal":3})
        interpreter=OpenAIInterpreter(key="k",opener=lambda *a,**k:io.BytesIO(json.dumps(body).encode()))
        with self.assertRaises(InterpretationError): interpreter.interpret("third",{"slot_count":2})
        with self.assertRaises(InterpretationError): interpreter.interpret("x"*20000,{})
