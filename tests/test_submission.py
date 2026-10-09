import unittest
from threading import Event, Thread
from appointment_assistant.submission import SubmissionGate, PendingSubmission, FailedSubmission, SubmissionCapacityError

class SubmissionTests(unittest.TestCase):
    def test_same_generation_once_and_distinct_generations(self):
        gate=SubmissionGate();calls=[]
        def work(): calls.append(1);return {"outcome":"unknown"}
        first=gate.execute(1,work)
        self.assertIs(gate.execute(1,work),first)
        gate.execute(2,work)
        self.assertEqual(len(calls),2)
    def test_concurrent_reentry_reserved_before_work(self):
        gate=SubmissionGate();entered=Event();release=Event();results=[];calls=[]
        def work(): calls.append(1);entered.set();release.wait(2);return "done"
        thread=Thread(target=lambda:results.append(gate.execute(1,work)));thread.start()
        self.assertTrue(entered.wait(1))
        self.assertIsInstance(gate.execute(1,work),PendingSubmission)
        release.set();thread.join(2)
        self.assertEqual(results,["done"]);self.assertEqual(calls,[1])
    def test_failure_reserved_without_exception_content(self):
        gate=SubmissionGate();calls=[]
        def work(): calls.append(1);raise RuntimeError("SECRET")
        with self.assertRaises(RuntimeError): gate.execute(1,work)
        receipt=gate.execute(1,work)
        self.assertIsInstance(receipt,FailedSubmission)
        self.assertNotIn("SECRET",repr(receipt));self.assertEqual(calls,[1])
    def test_invalid_and_capacity_do_not_replay(self):
        gate=SubmissionGate(limit=1);calls=[]
        for bad in (True,0,-1,"1"):
            with self.assertRaises(ValueError): gate.execute(bad,lambda:calls.append(1))
        gate.execute(1,lambda:"known")
        with self.assertRaises(SubmissionCapacityError): gate.execute(2,lambda:calls.append(1))
        self.assertEqual(gate.execute(1,lambda:calls.append(1)),"known")
        self.assertEqual(calls,[])
