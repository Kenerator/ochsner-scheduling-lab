"""Fixed ZEN proposed-action guard; the controller retains consent/effect authority.

Rules implement supplied Identity/Privacy and Booking policies plus the common
contract's identity-gated availability and unknown-write reconciliation boundary.
No identifiers or free-form content enter the engine.
"""
from dataclasses import dataclass
import json
from pathlib import Path
from threading import Lock

OPERATIONS = frozenset({"providers", "patient_search", "availability", "appointments", "book", "handoff", "medical_advice", "unsupported"})
CODES = frozenset({"allowed", "identity_required", "slot_required", "confirmation_required", "unknown_outcome", "medical_advice", "unsupported_request", "invalid_action", "policy_unavailable"})

@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    code: str

class PolicyGate:
    def __init__(self, path=None):
        self._decision = None
        self._lock = Lock()
        try:
            import zen
            document = Path(path) if path is not None else Path(__file__).resolve().parents[2] / "rules/safety.json"
            self._engine = zen.ZenEngine()
            self._decision = self._engine.create_decision(json.loads(document.read_text()))
        except Exception:
            # Fail closed; upstream exception text may contain paths or content.
            pass

    def _evaluate(self, facts):
        with self._lock:
            return self._decision.evaluate(facts)

    def evaluate(self, operation, verified=False, current_slot=False, current_consent=False, unknown=False):
        facts = dict(operation=operation, verified=verified, current_slot=current_slot, current_consent=current_consent, unknown=unknown)
        if not isinstance(operation, str) or operation not in OPERATIONS or any(type(facts[k]) is not bool for k in ("verified", "current_slot", "current_consent", "unknown")):
            return PolicyDecision(False, "invalid_action")
        try:
            result = self._evaluate(facts)["result"]
            if set(result) != {"allowed", "code"} or type(result["allowed"]) is not bool or result["code"] not in CODES or result["allowed"] != (result["code"] == "allowed"):
                raise ValueError("invalid policy result")
            return PolicyDecision(result["allowed"], result["code"])
        except Exception:
            return PolicyDecision(False, "policy_unavailable")
