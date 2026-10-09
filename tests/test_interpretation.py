import unittest
from appointment_assistant.interpretation import validate_action, RehearsalInterpreter, InterpretationError

FIELDS = dict.fromkeys(("phone","dob","zip_code","start_date","end_date","specialty","location"))
def payload(**changes):
    return dict(intent="book", fields=FIELDS.copy(), option_ordinal=None) | changes

class InterpretationTests(unittest.TestCase):
    def test_null_means_no_patch_and_closed_authority(self):
        self.assertEqual(validate_action(payload()).fields, FIELDS)
        for bad in (payload(confirmed=True), payload(fields=FIELDS | {"patientId":"p"}), payload(option_ordinal=True), payload(option_ordinal=0), payload(intent="invented"), payload(fields={})):
            with self.assertRaises(InterpretationError): validate_action(bad)

    def test_identity_dates_and_range_boundaries(self):
        for fields in ({"dob":"2025-02-29"}, {"zip_code":"7011x"}, {"phone":"x"*100}, {"start_date":"2026-10-20","end_date":"2026-10-19"}, {"specialty":"surgery"}):
            with self.subTest(fields=fields), self.assertRaises(InterpretationError): validate_action(payload(fields=FIELDS | fields))
        self.assertEqual(validate_action(payload(fields=FIELDS | {"dob":"2024-02-29","phone":"555-0101"})).fields["dob"], "2024-02-29")

    def test_rehearsal_extracts_patch_retains_intent_and_never_consent(self):
        interpreter=RehearsalInterpreter()
        action=interpreter.interpret("Phone 555-0101, DOB 1985-04-12 ZIP 70112", {"intent":"book"})
        self.assertEqual(action.intent,"book")
        self.assertEqual(action.fields["phone"],"555-0101")
        self.assertEqual(action.fields["dob"],"1985-04-12")
        self.assertEqual(action.fields["zip_code"],"70112")
        self.assertEqual(interpreter.interpret("second", {"intent":"book","slot_count":2}).option_ordinal,2)
        for text in ("yes","confirm"):
            action=interpreter.interpret(text,{"intent":"book"})
            self.assertEqual(action.intent,"unclear")
            self.assertTrue(all(v is None for v in action.fields.values()))

    def test_rehearsal_intents_and_supported_preferences(self):
        interpreter=RehearsalInterpreter()
        for text,want in (("Find primary care providers downtown","provider_lookup"),("Book dermatology uptown","book"),("Show my appointments","appointment_lookup"),("Talk to a human","human_request"),("What medicine should I take?","medical_advice")):
            with self.subTest(text=text): self.assertEqual(interpreter.interpret(text,{}).intent,want)

    def test_valid_out_of_range_choice_remains_a_proposal_for_local_validation(self):
        interpreter=RehearsalInterpreter()
        self.assertEqual(interpreter.interpret("9", {"intent":"book","slot_count":3}).option_ordinal,9)
