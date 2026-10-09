import unittest
from appointment_assistant.models import validate_provider, validate_patient, validate_slot, validate_appointment, validate_handoff, ValidationError

class RecordTests(unittest.TestCase):
    def test_provider_copy_and_closed_schema(self):
        record = dict(providerId="p", name="Dr Sample", specialty="primary_care", locations=["downtown"], modalities=["in_person"])
        copy = validate_provider(record)
        copy["locations"].append("uptown")
        self.assertEqual(record["locations"], ["downtown"])
        for patch in ({"locations": ["unknown"]}, {"providerId": ""}, {"modalities": ["unknown"]}, {"secret": "canary"}):
            with self.subTest(patch=patch), self.assertRaises(ValidationError): validate_provider(record | patch)

    def test_patient_validates_identity_without_eligibility_rule(self):
        record = dict(patientId="p", firstName="A", lastName="B", dateOfBirth="1985-04-12", phone="555-0101", zipCode="70112", establishedPatient=False)
        self.assertFalse(validate_patient(record)["establishedPatient"])
        for patch in ({"dateOfBirth":"2025-02-29"}, {"phone":"x"*100}, {"zipCode":"7011"}, {"establishedPatient":1}):
            with self.subTest(patch=patch), self.assertRaises(ValidationError): validate_patient(record | patch)

    def test_slot_and_appointment_require_aware_service_records(self):
        record = dict(slotId="s", providerId="p", specialty="dermatology", location="uptown", startTime="2026-10-20T09:00:00-05:00", available=True)
        self.assertEqual(validate_slot(record)["slotId"], "s")
        for patch in ({"available":False}, {"startTime":"2026-10-20T09:00:00"}, {"location":"invalid"}):
            with self.subTest(patch=patch), self.assertRaises(ValidationError): validate_slot(record | patch)
        appt = {k:v for k,v in record.items() if k not in ("slotId","available")}
        appt.update(appointmentId="a", patientId="pt", status="scheduled")
        self.assertEqual(validate_appointment(appt)["status"], "scheduled")
        with self.assertRaises(ValidationError): validate_appointment(appt | {"status":"pending"})

    def test_handoff_only_accepts_complete_queued_receipt(self):
        self.assertEqual(validate_handoff({"handoffId":"h", "status":"queued"})["status"], "queued")
        for value in ({"status":"queued"}, {"handoffId":"h", "status":"delivered"}, {"handoffId":"h", "status":"queued", "patientId":"p"}):
            with self.assertRaises(ValidationError): validate_handoff(value)
