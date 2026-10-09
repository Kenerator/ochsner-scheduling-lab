# Demo runbook

Updated2026-10-09. Use [README](../../README.md) setup. Required tests use the verified project interpreter; all flows use the unchanged supplied synthetic mock. CLI demos start fresh isolated server/store automatically; interactive UI shares its own server until restarted. No raw audit/transcript exports.

```sh
PATH="$PWD/.venv/bin:$PATH" PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python -m appointment_assistant --mode rehearsal --scenario success
PYTHONPATH=src .venv/bin/python -m appointment_assistant --mode rehearsal --scenario failure
```

Eight `--demo` names: provider_lookup, happy_path_booking, no_patient_match, multiple_patient_matches, appointment_lookup, slot_conflict, handoff, api_failure. Add `--json-summary` for whitelisted metadata, not chat or identity. api_failure sets the global supplied fault header; handoff also fails503.409 requires fresh selection and consent. POST timeout/malformed results are tested as unknown with no retries; these are injected transport doubles, not claims of live timeout.

## Tested evidence

Core integrated regression suite and all8 rehearsal demo acceptance tests passed during integration. Fresh MacARM and Linux authenticated clones at7e9f930 each passed90tests, cleaneditableinstall/pipcheck,all8demos andMarimocheck/startup. [Mac report](qualification-mac-arm.md), [Linux report](qualification-linux.md). Required rehearsal success/failure rerun at05:10UTC succeeded: confirmed booking after separate selection/consent; no-match ended with mock queued human request and no booking. Genuine [CLI live qualification](live-qualification.md) passed provider/book/no-match. Controlled IAB live form verified5turnbooking,2turnproviderclarification,reset/no-match/actualqueuedhandoff; LinuxcleancloneIABrehearsalverifiedprovider/book/separateconsent/reset/no-match/handoff. Upstream Marimo chat metadata defect was isolated and replaced with stable explicit form submission and immediate draft updates. Final responsive CSS affectedcheck passed at694px;10UItests+marimocheckpassed.

## Five-minute walkthrough

0:00 disclose AI/synthetic/local scope; show provider lookup.0:45 ask book primary care downtown, provide synthetic phone555-0101 and DOB1985-04-12 when asked.1:45 choose returned option; show exact summary and no POST until separate yes.2:15 show confirmed API appointment and guard/API evidence.2:45 reset conversation, demonstrate no-match555-9999/DOB1990-01-01 and truthful mock handoff.3:30 show global503 demo and direct staff next step.4:00 explain extraction versus deterministic authority, ZEN nonidentity facts, submission replay boundary and unknown outcome reconciliation.4:40 disclose Persona validation, production controls and recording/submission gaps.

Editing/selection/render/evidence reads must never dispatch. Restart only owned processes; no reset resolves unknown effects. Fixture times use fixed−05:00 and must be read from current API options, not assumed current calendar availability.
