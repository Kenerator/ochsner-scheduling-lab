# Code and test walkthrough

Updated: 2026-10-09. Reviewed product revision: `71f8e601e5666f15e4d3b3874e8d59537a089b35`; original product baseline; persona follow-on source is reviewed against committed adoption base c19680e plus the subsequent tested parser/support-summary delta. Controlled IAB repeated submission and responsive layout passed. Fresh Mac ARM/Linux installation and 90-test qualification are linked below.

## Follow a submitted turn

1. [CLI](../../../src/appointment_assistant/__main__.py) creates the shared dependencies and submits entered text. The [Marimo app](../../../apps/lab.py) uses a `text_area.form` callback through [FormAdapter.submit](../../../src/appointment_assistant/ui_adapter.py). Each explicit submission appends a user turn before dispatch; its internal `ChatAdapter.respond` derives a generation from user-turn count and caches the result. Identical text in distinct explicit submissions gets distinct generations. Read-only transcript/evidence rendering never calls `Session.submit`. The form avoids an upstream chat metadata defect; browser repeated-submit behavior is still being debugged.
2. [Session.submit](../../../src/appointment_assistant/conversation.py) delegates to [SubmissionGate.execute](../../../src/appointment_assistant/submission.py). The gate reserves under a lock before interpretation or HTTP work. A session lock serializes state transitions.
3. [OpenAIInterpreter.interpret](../../../src/appointment_assistant/openai_interpreter.py) makes one bounded Responses request; [validate_action](../../../src/appointment_assistant/interpretation.py) rejects extra authority fields, invalid enums/dates and invalid ordinal types. Rehearsal uses a separate visibly simulated interpreter.
4. The session applies field/intent corrections, increments revision and invalidates stale proposal/slots/known-result context. It gathers identity only for booking or appointments. Duplicate matches require private ZIP clarification without showing candidates.
5. `Session._guard` consumes [PolicyGate.evaluate](../../../src/appointment_assistant/policy.py). The packaged [ZEN table](../../../rules/safety.json) returns a fixed allowed/code verdict. Denial prevents the requested API effect; rule evaluation does not create patient or slot facts.
6. Availability comes from the scheduling service after verification. Returned slots are displayed; a later ordinal creates the exact proposal. A later whole-message `yes` or `confirm` can book only if patient, slot and revision still match. The proposal is cleared before dispatch. A successful service result becomes the known booking; 409 requires a fresh choice and consent, while an uncertain write blocks automatic retry.
7. [SchedulingAPI](../../../src/appointment_assistant/scheduling.py) validates requests/results, translates local date fields to supplied query names, disables redirects and makes one HTTP attempt. Known 409/503 responses differ from unreadable or mismatched POST results, which remain unknown. Only validated 201 writes complete. Its evidence route template omits patient path identifiers.
8. [Evidence.emit](../../../src/appointment_assistant/events.py) records closed metadata as immutable copies. [FormAdapter.evidence](../../../src/appointment_assistant/ui_adapter.py) reads the safe snapshot for the developer inspector.

## Test ownership and what it establishes

| Test file | Boundary exercised |
| --- | --- |
| [test_interpretation.py](../../../tests/test_interpretation.py) | Closed field patches, real calendar dates, intent preservation and labeled rehearsal |
| [test_openai_interpreter.py](../../../tests/test_openai_interpreter.py) | Strict Responses request, projected context, refusal/incomplete/duplicate/malformed output, safe errors without fallback |
| [test_models.py](../../../tests/test_models.py) | Returned provider/patient/slot/appointment/handoff shapes and copied records |
| [test_policy.py](../../../tests/test_policy.py) | Real ZEN decisions, all required booking facts, unknown-write block, invalid facts/document/engine/result fail closed |
| [test_events.py](../../../tests/test_events.py) | Closed core vocabulary, privacy canaries, route templates, copied bounded buffer/sinks, clock validation |
| [test_submission.py](../../../tests/test_submission.py) | Concurrent duplicate reservation, completed/unknown caching, failed receipt and capacity fail closed |
| [test_conversation.py](../../../tests/test_conversation.py) | Provider lookup without identity, multi-turn identification, current consent, corrections, ZIP, no-match, appointments, medical/outage/conflict and policy denial |
| [test_scheduling.py](../../../tests/test_scheduling.py) | Supplied-server roundtrip, input/query boundaries, 409/503, malformed data, unknown POST and no retries, date filter translation and diagnostic sink failure isolation (nine tests) |
| [test_cli.py](../../../tests/test_cli.py) | CLI modes and demonstration behavior; combined verification passed in fresh MacARM/Linux clones |
| [test_lab_ui.py](../../../tests/test_lab_ui.py) | Explicit form and internal cached receipt boundary, identical text as distinct submissions, render-only reads and sanitized failures; browser repeated-submit/remount qualification passed |

The 15 policy/evidence/submission tests passed against the local Python 3.11 virtual environment. Scheduling has nine focused tests; current CLI/demo and UI form boundary tests are present. All 24 conversation tests passed from the candidate root. This document does not assert a final passing combined suite. The integrating owner must record the authoritative final result. Unit doubles are not live AI evidence; supplied-service/live-model qualification belongs in [live qualification](../live-qualification.md).

The scaffold's [test_demo.py](../../../tests/test_demo.py) checks the original generic synthetic demo, not the scheduling feature acceptance. Do not treat its passing results as booking evidence.

## Verification entry points

After completing integration, run from the repository root using its explicit Python 3.11+ environment:

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python -m appointment_assistant --mode rehearsal --demo provider_lookup
PYTHONPATH=src .venv/bin/python -m appointment_assistant --mode rehearsal --demo happy_path_booking
PYTHONPATH=src .venv/bin/python -m appointment_assistant --mode rehearsal --demo no_patient_match
```

These entry points use the integrated scheduling adapter. Final combined acceptance is recorded by the integrating owner; browser behavior remains a separate qualification. Each CLI demo starts an isolated unchanged supplied reference server on an ephemeral loopback port and tears it down; live mode requires process-local `OPENAI_API_KEY`. `--json-summary` emits redacted metadata instead of transcript. Interactive UI/mock ports are documented in the final README/video notes after qualification.

## Small review modification exercise

A useful bounded exercise is to refine a fixed no-match follow-up message in `Session._turn`, preserving its state/outcome and finite human next step. First adjust the no-match assertion in `test_conversation.py`, confirm it detects the wording change, then update the message and run affected tests plus the full suite/no-match demo. No new API operation, clinical rule, identity disclosure or consent grammar is needed. This is a proposed exercise, not an already executed review event.

[Architecture](architecture.md) · [Native implementation tasks](../../../specs/001-appointment-assistant/tasks.md) · [Feature specification](../../../specs/001-appointment-assistant/spec.md)

Persona follow-on: schema-valid out-of-range ordinals reach deterministic current-choice validation, preserving visible options and identity without effects. Session builds fixed categorical support summaries separating known facts, missing information and persistent booking outcome; no identity values, IDs, dates or raw clinical/request text cross that summary boundary. [Persona choice integration tests](../../../tests/test_persona_choices.py) and [conversation tests](../../../tests/test_conversation.py) cover the repaired behavior; [live evidence](../live-qualification.md) records actual keyboard/UI checks.
