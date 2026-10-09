"""Ellie-Rae regression through real extraction and isolated supplied API."""
import unittest
from appointment_assistant.conversation import Session
from appointment_assistant.interpretation import RehearsalInterpreter
from appointment_assistant.scheduling import SchedulingAPI
from tests.helpers import reference_server

class PersonaChoiceTests(unittest.TestCase):
    def test_invalid_number_preserves_identity_choices_and_separate_consent(self):
        server,thread,store=reference_server()
        try:
            session=Session(SchedulingAPI('http://127.0.0.1:'+str(server.server_port)),RehearsalInterpreter())
            first=session.submit('Book primary care downtown phone 555-0101 DOB 1985-04-12')
            self.assertEqual(first.state,'slots')
            patient=session.patient.copy();slots=session.slots.copy()
            before=len(store.appointments)
            invalid=session.submit('9')
            self.assertEqual(invalid.state,'slots')
            self.assertIn('Choose a numbered option',invalid.message)
            self.assertIn('1.',invalid.message)
            self.assertEqual(session.patient,patient)
            self.assertEqual(session.slots,slots)
            self.assertEqual(len(store.appointments),before)
            proposal=session.submit('1')
            self.assertEqual(proposal.state,'proposal')
            self.assertNotIn('provide your',proposal.message.lower())
            self.assertEqual(len(store.appointments),before)
            self.assertEqual(session.submit('yes').state,'booked')
            self.assertEqual(len(store.appointments),before+1)
        finally:
            server.shutdown();server.server_close();thread.join(2)
