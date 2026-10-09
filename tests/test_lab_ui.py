"""UI submission tests use a counting core boundary, not Marimo internals."""
from types import SimpleNamespace
import unittest
from appointment_assistant.ui_adapter import ChatAdapter

class Events:
    def __init__(self): self.reads=0
    def snapshot(self): self.reads+=1; return [{"category":"guard","allowed":True}]
class CountingSession:
    def __init__(self,fail=False): self.calls=[]; self.events=Events(); self.fail=fail
    def submit(self,text,generation):
        self.calls.append((text,generation))
        if self.fail: raise RuntimeError("private-canary")
        return SimpleNamespace(message="Receipt "+str(generation))
def user(text): return SimpleNamespace(role="user",content=text)
def assistant(text): return SimpleNamespace(role="assistant",content=text)

class ChatBoundaryTests(unittest.TestCase):
    def test_reactive_reentry_and_edited_history_cannot_repeat_effect(self):
        session=CountingSession(); adapter=ChatAdapter(session)
        history=[user("book")]
        self.assertEqual(adapter.respond(history),"Receipt 1")
        self.assertEqual(adapter.respond(history),"Receipt 1")
        self.assertEqual(adapter.respond([user("edited unsent history")]),"Receipt 1")
        self.assertEqual(session.calls,[("book",1)])

    def test_repeated_text_new_explicit_user_message_is_new_generation(self):
        session=CountingSession(); adapter=ChatAdapter(session)
        self.assertEqual(adapter.respond([user("yes")]),"Receipt 1")
        self.assertEqual(adapter.respond([user("yes"),assistant("known outcome"),user("yes")]),"Receipt 2")
        self.assertEqual(session.calls,[("yes",1),("yes",2)])

    def test_empty_assistant_and_evidence_reads_cause_no_submission(self):
        session=CountingSession(); adapter=ChatAdapter(session)
        adapter.respond([])
        adapter.respond([assistant("hello")])
        self.assertEqual(adapter.evidence(),[{"category":"guard","allowed":True}])
        self.assertEqual(adapter.evidence(),[{"category":"guard","allowed":True}])
        self.assertEqual(session.calls,[])

    def test_exception_receipt_is_cached_and_sanitized(self):
        session=CountingSession(fail=True); adapter=ChatAdapter(session)
        message=adapter.respond([user("private-utterance")])
        self.assertNotIn("private",message)
        self.assertEqual(adapter.respond([user("retry")]),message)
        self.assertEqual(len(session.calls),1)

    def test_pending_and_failed_core_receipts_are_safe(self):
        for status in ("in_progress","failed"):
            class Session(CountingSession):
                def submit(self,text,generation): return SimpleNamespace(status=status)
            message=ChatAdapter(Session()).respond([user("hello")])
            self.assertIsInstance(message,str)
            self.assertTrue(message)

class FormBoundaryTests(unittest.TestCase):
    def test_explicit_identical_form_submissions_get_distinct_generations(self):
        from appointment_assistant.ui_adapter import FormAdapter
        session=CountingSession(); adapter=FormAdapter(session)
        adapter.submit('yes'); adapter.submit('yes')
        self.assertEqual(session.calls,[('yes',1),('yes',2)])
        self.assertEqual(adapter.transcript(),[('yes','Receipt 1'),('yes','Receipt 2')])

    def test_form_reads_and_none_callback_do_not_submit(self):
        from appointment_assistant.ui_adapter import FormAdapter
        session=CountingSession(); adapter=FormAdapter(session)
        adapter.submit(None)
        adapter.transcript(); adapter.evidence(); adapter.transcript()
        self.assertEqual(session.calls,[])

    def test_form_dispatch_exception_is_safe_and_generation_never_reopened(self):
        from appointment_assistant.ui_adapter import FormAdapter
        session=CountingSession(fail=True); adapter=FormAdapter(session)
        adapter.submit('private-canary')
        self.assertNotIn('private',adapter.transcript()[0][1])
        adapter.transcript(); adapter.evidence()
        self.assertEqual(session.calls,[('private-canary',1)])

    def test_pinned_marimo_form_accepts_repeat_submit_without_chat_metadata(self):
        """Characterize the chosen replacement at the same-value event boundary."""
        import marimo as mo
        from appointment_assistant.ui_adapter import FormAdapter
        session=CountingSession(); adapter=FormAdapter(session)
        form=mo.ui.text_area().form(on_change=adapter.submit,clear_on_submit=True)
        form._update('yes'); form._update('yes')
        self.assertEqual(session.calls,[('yes',1),('yes',2)])

class AppInputBoundaryTests(unittest.TestCase):
    def test_app_typing_updates_input_without_blur_and_waits_for_send(self):
        """Debounced textarea edits can make the first click submit a stale value."""
        import runpy
        from pathlib import Path
        import marimo as mo
        from appointment_assistant.ui_adapter import FormAdapter
        session=CountingSession(); adapter=FormAdapter(session)
        app=runpy.run_path(str(Path(__file__).resolve().parents[1]/'apps/lab.py'))['app']
        cell=next(cell for cell in app._cell_manager.cells() if 'request_form' in cell.defs)
        _,definitions=cell.run(adapter=adapter,mo=mo,set_submission_revision=lambda _:None)
        form=definitions['request_form']
        self.assertIs(form.element._args.args['debounce'],False)
        form.element._update('Find primary care providers downtown')
        self.assertEqual(session.calls,[])
        form._update(form.element.value)
        self.assertEqual(session.calls,[('Find primary care providers downtown',1)])
