"""Session-only explicit-submission receipts; no API idempotency is implied.

Inspired by nxus.SYSTEMS Reasoning Lab AnalysisSubmissionGate; MIT notice in
licenses/nxusKit-examples-MIT.txt. Reservations precede all execution here.
"""
from dataclasses import dataclass
from threading import Lock

@dataclass(frozen=True)
class PendingSubmission:
    status: str = "in_progress"

@dataclass(frozen=True)
class FailedSubmission:
    status: str = "failed"
    code: str = "submission_failed"

class SubmissionCapacityError(RuntimeError):
    pass

class SubmissionGate:
    def __init__(self, limit=200):
        if type(limit) is not int or limit < 1:
            raise ValueError("invalid submission limit")
        self._limit = limit
        self._receipts = {}
        self._lock = Lock()

    def execute(self, generation, thunk):
        if type(generation) is not int or generation < 1:
            raise ValueError("invalid submission generation")
        with self._lock:
            if generation in self._receipts:
                return self._receipts[generation]
            if len(self._receipts) >= self._limit:
                # Never prune a reservation: pruning would permit effect replay.
                raise SubmissionCapacityError("session submission capacity reached")
            self._receipts[generation] = PendingSubmission()
        try:
            result = thunk()
        except BaseException:
            with self._lock:
                self._receipts[generation] = FailedSubmission()
            raise
        with self._lock:
            self._receipts[generation] = result
        return result
