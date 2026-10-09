import unittest
from unittest.mock import patch
from appointment_assistant.policy import PolicyGate

class PolicyTests(unittest.TestCase):
    def test_real_engine_public_operations(self):
        gate = PolicyGate()
        for op in ("providers", "patient_search", "handoff"):
            self.assertTrue(gate.evaluate(op).allowed, op)
    def test_patient_reads_need_verified_identity(self):
        gate = PolicyGate()
        for op in ("availability", "appointments"):
            self.assertEqual(gate.evaluate(op).code, "identity_required")
            self.assertTrue(gate.evaluate(op, verified=True).allowed)
    def test_booking_all_facts_and_unknown_override(self):
        gate = PolicyGate()
        facts = dict(verified=True, current_slot=True, current_consent=True)
        self.assertTrue(gate.evaluate("book", **facts).allowed)
        for key in facts:
            self.assertFalse(gate.evaluate("book", **{**facts,key:False}).allowed)
        self.assertEqual(gate.evaluate("book", **facts, unknown=True).code,"unknown_outcome")
    def test_invalid_and_unsupported_actions(self):
        gate = PolicyGate()
        for op in ("medical_advice", "unsupported", "arbitrary-secret", None):
            self.assertFalse(gate.evaluate(op).allowed)
        for value in (1, "true", None):
            self.assertEqual(gate.evaluate("book",verified=value).code,"invalid_action")
    def test_engine_or_document_failure_is_closed(self):
        self.assertEqual(PolicyGate("/nonexistent/safety.json").evaluate("providers").code,"policy_unavailable")
        gate = PolicyGate()
        with patch.object(gate, "_evaluate", side_effect=RuntimeError("SECRET")):
            result = gate.evaluate("providers")
        self.assertFalse(result.allowed)
        self.assertEqual(result.code,"policy_unavailable")
        self.assertNotIn("SECRET",repr(result))

    def test_malformed_or_contradictory_engine_result_is_closed(self):
        gate=PolicyGate()
        for result in ({"allowed":True,"code":"identity_required"},{"allowed":True,"code":"allowed","raw":"SECRET"},{"allowed":1,"code":"allowed"},None):
            with patch.object(gate,"_evaluate",return_value={"result":result}):
                verdict=gate.evaluate("providers")
                self.assertFalse(verdict.allowed)
                self.assertEqual(verdict.code,"policy_unavailable")
