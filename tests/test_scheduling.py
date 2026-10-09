"""Real unchanged supplied API, isolated stores, and hostile transport cases."""
import importlib.util
import io
import json
import threading
import unittest
from contextlib import contextmanager
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from appointment_assistant.scheduling import SchedulingAPI, SchedulingError

spec = importlib.util.spec_from_file_location('supplied_mock', Path(__file__).resolve().parents[1] / 'vendor/reference-api/mock-api/server.py')
mock = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mock)

@contextmanager
def supplied_server():
    class Quiet(mock.Handler):
        store = mock.Store()
        calls = []
        def audit(self, method, path, status, ms): self.calls.append((method, status))
    server = ThreadingHTTPServer(('127.0.0.1', 0), Quiet)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try: yield 'http://127.0.0.1:%s' % server.server_port, Quiet
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

class Response(io.BytesIO):
    def __init__(self, payload, status=200):
        super().__init__(payload if isinstance(payload, bytes) else json.dumps(payload).encode())
        self.status = status

class Events:
    def __init__(self): self.rows = []
    def emit(self, kind, **fields): self.rows.append(dict(kind=kind, **fields))

class SchedulingTests(unittest.TestCase):
    def test_supplied_roundtrip_redacted(self):
        with supplied_server() as (url, handler):
            events = Events()
            api = SchedulingAPI(url, events=events)
            self.assertEqual(len(api.providers(specialty='primary_care', location='downtown')), 2)
            self.assertEqual(api.search_patients('555-0101', '1985-04-12')[0]['patientId'], 'pat_1001')
            self.assertEqual(len(api.search_patients('555-0130', '1978-09-22')), 2)
            self.assertEqual(api.search_patients('555-0000', '1985-04-12'), [])
            slot = api.availability('pat_1001', specialty='primary_care', location='downtown')[0]
            result = api.book('pat_1001', slot)
            self.assertEqual(result['status'], 'scheduled')
            self.assertEqual(result['startTime'], slot['startTime'])
            self.assertIn(result, api.appointments('pat_1001'))
            self.assertEqual(api.handoff('user_requested', 'User requested scheduling assistance.', 'pat_1001')['status'], 'queued')
            self.assertEqual(len(handler.store.handoffs), 1)
            for private in ('555-0101', 'pat_1001', '1985-04-12'): self.assertNotIn(private, repr(events.rows))
            self.assertIn('/patients/{patientId}/appointments', [r['route'] for r in events.rows])

    def test_conflict_and_all_outages_no_retry(self):
        with supplied_server() as (url, handler):
            api = SchedulingAPI(url)
            slot = next(s for s in api.availability('pat_1001', specialty='primary_care') if s['slotId'] == 'slot_conflict_001')
            with self.assertRaises(SchedulingError) as err: api.book('pat_1001', slot)
            self.assertEqual(err.exception.status, 409)
            self.assertFalse(err.exception.unknown)
            outage = SchedulingAPI(url, scenario='api_failure')
            for action in [lambda: outage.providers(), lambda: outage.search_patients('555-0101', '1985-04-12'), lambda: outage.availability('pat_1001', specialty='primary_care'), lambda: outage.appointments('pat_1001'), lambda: outage.book('pat_1001', slot), lambda: outage.handoff('api_failure', 'Scheduling unavailable.')]:
                with self.assertRaises(SchedulingError) as err: action()
                self.assertEqual(err.exception.status, 503)
                self.assertFalse(err.exception.unknown)
            self.assertEqual(len(handler.calls), 8)
            self.assertEqual(len(handler.store.appointments), 2)

    def test_invalid_before_io(self):
        calls = []
        api = SchedulingAPI(opener=lambda *a, **k: calls.append(a))
        for action in [lambda: api.providers(specialty='cardiology'), lambda: api.providers(zip='70112'), lambda: api.search_patients('555-0101', '2026-02-30'), lambda: api.availability('pat_1001', specialty='primary_care', startDate='2026-12-01', endDate='2026-01-01'), lambda: api.book('pat_1001', {}), lambda: api.handoff('bad', 'Hello'), lambda: api.appointments('../private')]:
            with self.assertRaises(SchedulingError): action()
        self.assertEqual(calls, [])
        for timeout in (0, -1, float('inf'), float('nan'), True):
            with self.assertRaises(SchedulingError): SchedulingAPI(timeout=timeout)

    def test_literal_query_encoding(self):
        calls = []
        def opener(req, timeout):
            calls.append(req)
            return Response({'matches': []})
        SchedulingAPI(opener=opener).search_patients('+1 5550101', '1985-04-12')
        self.assertEqual(parse_qs(urlsplit(calls[0].full_url).query), {'phone': ['+1 5550101'], 'dob': ['1985-04-12']})

    def test_unknown_post_never_retry(self):
        with supplied_server() as (url, handler): slot = SchedulingAPI(url).availability('pat_1001', specialty='primary_care')[0]
        appointment = dict(appointmentId='a1', patientId='pat_1001', status='scheduled', **{k: slot[k] for k in ('providerId', 'specialty', 'location', 'startTime')})
        for response in (TimeoutError('PRIVATE CANARY'), Response(b'not json', 201), Response({'appointment': dict(appointment, patientId='another')}, 201), Response({'appointment': appointment}, 200), Response(b'x' * 1100000, 201)):
            calls = []
            def opener(req, timeout):
                calls.append(req)
                if isinstance(response, Exception): raise response
                return response
            events = Events()
            with self.assertRaises(SchedulingError) as err: SchedulingAPI(opener=opener, events=events).book('pat_1001', slot)
            self.assertTrue(err.exception.unknown)
            self.assertEqual(len(calls), 1)
            self.assertNotIn('PRIVATE CANARY', str(err.exception))
            self.assertEqual(events.rows[-1]['outcome'], 'unknown')
            self.assertIs(json.loads(calls[0].data)['confirmed'], True)

    def test_get_malformed_and_mismatched_fail(self):
        for payload in ({}, {'providers': None}, {'providers': [dict(mock.Store().providers[0], specialty='dermatology')]}, {'providers': [dict(mock.Store().providers[0], conflictOnBooking=True)]}):
            with self.assertRaises(SchedulingError) as err: SchedulingAPI(opener=lambda *a, **k: Response(payload)).providers(specialty='primary_care')
            self.assertFalse(err.exception.unknown)
        with self.assertRaises(SchedulingError): SchedulingAPI(opener=lambda *a, **k: Response({'matches': mock.Store().patients})).search_patients('555-0101', '1985-04-12')

    def test_diagnostic_failure_cannot_change_completed_effect(self):
        class BrokenEvents:
            def emit(self, *args, **kwargs): raise RuntimeError('PRIVATE SINK')
        with supplied_server() as (url, handler):
            api = SchedulingAPI(url, events=BrokenEvents())
            slot = SchedulingAPI(url).availability('pat_1001', specialty='primary_care')[0]
            result = api.book('pat_1001', slot)
            self.assertEqual(result['status'], 'scheduled')
            self.assertEqual(len(handler.store.appointments), 3)

    def test_handoff_unknown_and_appointment_attribute_mismatch(self):
        with supplied_server() as (url, handler):
            slot = SchedulingAPI(url).availability('pat_1001', specialty='primary_care')[0]
        appointment = dict(appointmentId='a1', patientId='pat_1001', status='scheduled', **{k: slot[k] for k in ('providerId','specialty','location','startTime')})
        for key, value in (('providerId','different'), ('specialty','dermatology'), ('location','lakeside'), ('startTime','2030-01-01T12:00:00-05:00'), ('status','cancelled')):
            with self.assertRaises(SchedulingError) as err:
                SchedulingAPI(opener=lambda *a, **k: Response({'appointment': dict(appointment, **{key:value})}, 201)).book('pat_1001', slot)
            self.assertTrue(err.exception.unknown)
        for payload in ({'handoffId':'h1','status':'delivered'}, {'handoffId':'','status':'queued'}, {'status':'queued'}):
            with self.assertRaises(SchedulingError) as err:
                SchedulingAPI(opener=lambda *a, **k: Response(payload, 201)).handoff('other','Scheduling assistance required.')
            self.assertTrue(err.exception.unknown)

    def test_core_date_filter_names_translate_to_supplied_query(self):
        calls = []
        def opener(req, timeout):
            calls.append(req)
            return Response({'slots': []})
        api = SchedulingAPI(opener=opener)
        self.assertEqual(api.availability('pat_1001',specialty='primary_care',start_date='2030-01-01',end_date='2030-02-01'), [])
        query = parse_qs(urlsplit(calls[0].full_url).query)
        self.assertEqual(query['startDate'], ['2030-01-01'])
        self.assertEqual(query['endDate'], ['2030-02-01'])
        self.assertNotIn('start_date', query)
        with self.assertRaises(SchedulingError): api.availability('pat_1001', specialty='primary_care',start_date='2030-01-01',startDate='2030-01-01')

if __name__ == '__main__': unittest.main()
