"""Construct bounded safe metadata; never copy/redact arbitrary source payloads.

Inspired by nxus.SYSTEMS Reasoning Lab run_events.py; MIT license retained in
licenses/nxusKit-examples-MIT.txt. No raw identity/content fields are accepted.
"""
from collections import deque
from copy import deepcopy
from datetime import datetime, timezone
import math
from threading import Lock
from uuid import uuid4

CATEGORIES = {"interpretation", "workflow", "guard", "api", "handoff", "latency"}
CODES = {"allowed", "policy_unavailable", "invalid_action", "model_unavailable", "api_failure", "identity_unclear", "medical_advice", "no_availability", "user_requested", "unsupported_request", "slot_conflict", "unknown_outcome", "confirmation_required", "identity_required", "slot_required"}
ENUMS = {
 "intent": {"provider_lookup", "book", "appointment_lookup", "human_request", "medical_advice", "unsupported", "decline", "reset", "unclear"},
 "state": {"start", "clarify", "identity", "preferences", "slots", "proposal", "providers", "appointments", "blocked", "conflict", "idle", "gathering", "identifying", "identity_required", "identity_ambiguous", "verified", "searching", "choosing", "awaiting_confirmation", "booked", "handoff", "stopped", "unknown"},
 "action": {"providers", "patient_search", "appointments", "lookup", "availability", "book", "handoff", "none"},
 "code": CODES, "reason": CODES | {"other"},
 "method": {"GET", "POST"},
 "route": {"/providers", "/patients/search", "/availability", "/patients/{patientId}/appointments", "/appointments", "/handoffs"},
 "outcome": {"not_attempted", "attempted", "completed", "rejected", "failed", "unknown", "queued", "accepted", "received", "started", "stopped"},
}
FIELDS = set(ENUMS) | {"allowed", "status", "option_count", "elapsed_ms"}

class Evidence:
    def __init__(self, sink=None, clock=None, limit=200):
        if type(limit) is not int or limit < 1:
            raise ValueError("invalid evidence limit")
        self._sink = sink
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._events = deque(maxlen=limit)
        self._sequence = 0
        self._session_id = uuid4().hex
        self._lock = Lock()

    def emit(self, category, **fields):
        if category not in CATEGORIES or not set(fields) <= FIELDS:
            raise ValueError("invalid evidence fields")
        for key, value in fields.items():
            if key in ENUMS:
                valid = isinstance(value, str) and value in ENUMS[key]
            elif key == "allowed":
                valid = type(value) is bool
            elif key == "status":
                valid = type(value) is int and 100 <= value <= 599
            elif key == "option_count":
                valid = type(value) is int and 0 <= value <= 10000
            else:
                valid = type(value) in (float, int) and math.isfinite(value) and 0 <= value <= 86400000
            if not valid:
                raise ValueError("invalid evidence value")
        now = self._clock()
        if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("evidence clock must return aware datetime")
        with self._lock:
            self._sequence += 1
            event = dict(session_id=self._session_id, sequence=self._sequence, timestamp_utc=now.astimezone(timezone.utc).isoformat(), category=category, **fields)
            self._events.append(event)
        if self._sink is not None:
            try:
                self._sink(deepcopy(event))
            except Exception:
                # Diagnostic sink failure must not turn a completed write into replay.
                pass
        return deepcopy(event)

    def snapshot(self):
        with self._lock:
            return deepcopy(list(self._events))
