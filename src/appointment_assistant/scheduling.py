"""Bounded scheduling HTTP boundary; the deterministic core owns consent/identity."""
import json
import math
import re
import time
from urllib.error import HTTPError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

from .models import (LOCATIONS, SPECIALTIES, ValidationError, valid_date, valid_phone,
                     validate_provider, validate_patient, validate_slot,
                     validate_appointment, validate_handoff)

MAX_RESPONSE = 1024 * 1024
MAX_REQUEST = 4096
REASONS = ('user_requested', 'identity_unclear', 'unsupported_request',
           'medical_advice', 'api_failure', 'no_availability', 'other')

class SchedulingError(Exception):
    """Closed error metadata, deliberately excluding upstream text and identifiers."""
    def __init__(self, code='unavailable', status=None, unknown=False):
        if code not in ('invalid_input', 'rejected', 'conflict', 'unavailable', 'unknown'):
            code = 'unknown' if unknown else 'unavailable'
        self.code = code
        self.status = status if type(status) is int else None
        self.unknown = bool(unknown)
        super().__init__(code)

class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # An effect response must never cause another automatic request.

def _identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', value):
        raise SchedulingError('invalid_input')
    return value

def _input_validate(validator, value):
    try:
        return validator(value)
    except (ValueError, TypeError, KeyError):
        raise SchedulingError('invalid_input') from None

class SchedulingAPI:
    def __init__(self, base_url='http://127.0.0.1:4013', events=None,
                 scenario=None, timeout=15, opener=None):
        try:
            parsed = urlsplit(base_url)
            if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
                raise ValueError()
            if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0 or timeout > 120:
                raise ValueError()
            if scenario not in (None, 'api_failure'):
                raise ValueError()
        except (ValueError, TypeError):
            raise SchedulingError('invalid_input') from None
        self.base_url = base_url.rstrip('/')
        self.events = events
        self.scenario = scenario
        self.timeout = timeout
        self.opener = opener or build_opener(_NoRedirect()).open

    def _request(self, method, path, validate, query=None, body=None, route=None):
        raw = None if body is None else json.dumps(body, separators=(',', ':')).encode('utf-8')
        if raw is not None and len(raw) > MAX_REQUEST:
            raise SchedulingError('invalid_input')
        url = self.base_url + path + ('?' + urlencode(query) if query else '')
        headers = {'Accept': 'application/json'}
        if raw is not None: headers['Content-Type'] = 'application/json'
        if self.scenario: headers['X-Mock-Scenario'] = self.scenario
        request = Request(url, data=raw, headers=headers, method=method)
        started = time.monotonic()
        status = None
        outcome = 'failed'
        try:
            try:
                response = self.opener(request, timeout=self.timeout)
            except HTTPError as error:
                status = error.code
                error.close()
                response = None
            if response is not None:
                try:
                    status = response.status
                    if type(status) is not int: raise ValueError()
                    # Do not read error payloads: status alone supplies the closed outcome.
                    data = response.read(MAX_RESPONSE + 1) if status == (201 if method == 'POST' else 200) else b''
                finally:
                    response.close()
            if status in (400, 404, 409, 503):
                outcome = 'rejected'
                raise SchedulingError('conflict' if status == 409 else 'rejected', status)
            if status != (201 if method == 'POST' else 200): raise ValueError()
            if len(data) > MAX_RESPONSE: raise ValueError()
            payload = json.loads(data.decode('utf-8'))
            result = validate(payload)
            outcome = 'completed'
            return result
        except SchedulingError:
            raise
        except Exception:
            # Once a POST is dispatched, unreadable/mismatched results require reconciliation.
            outcome = 'unknown' if method == 'POST' else 'failed'
            raise SchedulingError('unknown' if method == 'POST' else 'unavailable', status, method == 'POST') from None
        finally:
            if self.events is not None:
                fields = dict(method=method, route=route or path, outcome=outcome,
                              elapsed_ms=round((time.monotonic() - started) * 1000, 3))
                if type(status) is int: fields['status'] = status
                try:
                    self.events.emit('api', **fields)
                except Exception:
                    # Evidence failures cannot erase a completed effect or trigger replay.
                    pass

    @staticmethod
    def _list(payload, key, validator, matches=lambda record: True):
        if not isinstance(payload, dict) or set(payload) != {key} or not isinstance(payload[key], list):
            raise ValidationError('Invalid envelope')
        result = [validator(item) for item in payload[key]]
        if any(not matches(item) for item in result): raise ValidationError('Mismatched record')
        return result

    @staticmethod
    def _filters(filters, availability=False):
        filters = dict(filters)
        if availability:
            # Core field names remain Python-style; wire names follow supplied OpenAPI.
            for local, wire in (('start_date', 'startDate'), ('end_date', 'endDate')):
                if local in filters:
                    if wire in filters: raise SchedulingError('invalid_input')
                    filters[wire] = filters.pop(local)
        allowed = {'specialty', 'location'} | ({'startDate', 'endDate'} if availability else set())
        if set(filters) - allowed: raise SchedulingError('invalid_input')
        if availability and 'specialty' not in filters: raise SchedulingError('invalid_input')
        for key, value in filters.items():
            if key in ('startDate', 'endDate'):
                _input_validate(valid_date, value)
            elif not isinstance(value, str) or value not in (SPECIALTIES if key == 'specialty' else LOCATIONS):
                raise SchedulingError('invalid_input')
        if 'startDate' in filters and 'endDate' in filters and filters['startDate'] > filters['endDate']:
            raise SchedulingError('invalid_input')
        return dict(filters)

    def providers(self, **filters):
        filters = self._filters(filters)
        def matches(item):
            return (('specialty' not in filters or item['specialty'] == filters['specialty']) and
                    ('location' not in filters or filters['location'] in item['locations']))
        return self._request('GET', '/providers', lambda p: self._list(p, 'providers', validate_provider, matches), query=filters)

    def search_patients(self, phone, dob):
        _input_validate(valid_phone, phone)
        _input_validate(valid_date, dob)
        return self._request('GET', '/patients/search', lambda p: self._list(p, 'matches', validate_patient,
                             lambda item: item['phone'] == phone and item['dateOfBirth'] == dob),
                             query={'phone': phone, 'dob': dob})

    def availability(self, patient_id, **filters):
        _identifier(patient_id)
        filters = self._filters(filters, availability=True)
        def matches(item):
            return (item['specialty'] == filters['specialty'] and
                    ('location' not in filters or item['location'] == filters['location']) and
                    ('startDate' not in filters or item['startTime'][:10] >= filters['startDate']) and
                    ('endDate' not in filters or item['startTime'][:10] <= filters['endDate']))
        return self._request('GET', '/availability', lambda p: self._list(p, 'slots', validate_slot, matches),
                             query=dict(patientId=patient_id, **filters))

    def appointments(self, patient_id):
        _identifier(patient_id)
        return self._request('GET', '/patients/' + quote(patient_id, safe='') + '/appointments',
                             lambda p: self._list(p, 'appointments', validate_appointment,
                             lambda item: item['patientId'] == patient_id), route='/patients/{patientId}/appointments')

    def book(self, patient_id, slot):
        _identifier(patient_id)
        slot = _input_validate(validate_slot, slot)
        def validate(payload):
            if not isinstance(payload, dict) or set(payload) != {'appointment'}: raise ValidationError('Invalid envelope')
            result = validate_appointment(payload['appointment'])
            if result['patientId'] != patient_id or any(result[k] != slot[k] for k in ('providerId', 'specialty', 'location', 'startTime')):
                raise ValidationError('Mismatched appointment')
            return result
        return self._request('POST', '/appointments', validate,
                             body={'patientId': patient_id, 'slotId': slot['slotId'], 'confirmed': True})

    def handoff(self, reason, summary, patient_id=None):
        if reason not in REASONS or not isinstance(summary, str) or not summary.strip() or len(summary) > 300:
            raise SchedulingError('invalid_input')
        # Core supplies fixed summaries; defense in depth rejects common identifier forms.
        if re.search(r'\d|pat_|@|[\r\n]', summary): raise SchedulingError('invalid_input')
        body = {'reason': reason, 'summary': summary}
        if patient_id is not None: body['patientId'] = _identifier(patient_id)
        return self._request('POST', '/handoffs', validate_handoff, body=body)
