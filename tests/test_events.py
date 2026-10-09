import unittest
from datetime import datetime, timezone
from appointment_assistant.events import Evidence

class EvidenceTests(unittest.TestCase):
    def test_closed_projection_copies_and_bound(self):
        sink=[]
        evidence=Evidence(sink.append, clock=lambda:datetime(2026,1,1,tzinfo=timezone.utc),limit=2)
        evidence.emit("guard",action="book",code="confirmation_required",allowed=False)
        evidence.emit("api",method="GET",route="/patients/{patientId}/appointments",status=200,elapsed_ms=1.5)
        evidence.emit("workflow",state="idle",outcome="not_attempted")
        self.assertEqual(len(evidence.snapshot()),2)
        self.assertEqual(evidence.snapshot()[0]["sequence"],2)
        sink[1]["status"]=500
        snapshot=evidence.snapshot();snapshot[0]["status"]=400
        self.assertEqual(evidence.snapshot()[0]["status"],200)
        self.assertTrue(evidence.snapshot()[0]["session_id"])
    def test_canaries_unknown_keys_values_routes_rejected(self):
        evidence=Evidence()
        bad=[("guard",dict(prompt="SECRET")),("api",dict(route="/patients/pat-secret/appointments")),("workflow",dict(state="SECRET")),("guard",dict(code="SECRET")),("interpretation",dict(intent="SECRET")),("api",dict(status=True)),("latency",dict(elapsed_ms=float("nan")))]
        for category,fields in bad:
            with self.assertRaises(ValueError): evidence.emit(category,**fields)
        self.assertEqual(evidence.snapshot(),[])
    def test_sink_mutation_and_failure_do_not_change_evidence(self):
        def sink(event):
            event["code"]="SECRET"
            raise RuntimeError("SECRET")
        evidence=Evidence(sink)
        evidence.emit("guard",code="allowed",allowed=True)
        self.assertEqual(evidence.snapshot()[0]["code"],"allowed")
    def test_invalid_category_limit_clock(self):
        with self.assertRaises(ValueError): Evidence(limit=0)
        with self.assertRaises(ValueError): Evidence().emit("SECRET")
        with self.assertRaises(ValueError): Evidence(clock=lambda:datetime(2026,1,1)).emit("guard")

    def test_agreed_core_metadata_vocabulary(self):
        evidence=Evidence()
        for state in ("start","clarify","identity","preferences","slots","proposal","providers","appointments","booked","handoff","blocked","conflict"):
            evidence.emit("workflow",state=state,outcome="not_attempted")
        for action in ("providers","patient_search","availability","appointments","book","handoff"):
            evidence.emit("guard",action=action,code="allowed",allowed=True)
        for intent in ("provider_lookup","book","appointment_lookup","human_request","medical_advice","unsupported","decline","reset","unclear"):
            evidence.emit("interpretation",intent=intent,action="none",outcome="completed")
        for reason in ("user_requested","identity_unclear","unsupported_request","medical_advice","api_failure","no_availability","other"):
            evidence.emit("handoff",reason=reason,outcome="not_attempted")
