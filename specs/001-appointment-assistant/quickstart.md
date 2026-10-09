# Implementation validation quickstart

Updated: 2026-10-09. Implement is in progress. This guide defines acceptance commands; Plan itself did not implement the application. Qualification remains pending until evidence is recorded in [tasks.md](tasks.md) and the linked qualification documents.

## Prerequisites and setup

Use an explicit Python 3.11+ executable on Mac ARM and Linux. From repository root:

```sh
python3.11 -c 'import sys; assert sys.version_info >= (3, 11); print(sys.version)'
python3.11 -m venv .venv
.venv/bin/python -m pip install -e .
```

Project dependencies declare `marimo==0.25.1` and `zen-engine==2.1.2`; editable installation installs both pins. Preserve managed bootstrap controls. Live mode needs reviewer-configured `OPENAI_API_KEY` environment and network/model account access; do not put key values in files, command arguments or logs. Rehearsal needs no credentials and must be visibly labeled. Historical Plan performed no credential access/live test; current live qualification uses only the existing local-live grant.

## Start local components

In separate terminals, after selective vendoring/implementation:

```sh
.venv/bin/python vendor/reference-api/mock-api/server.py --port 4013
PYTHONPATH=src .venv/bin/python -m marimo run apps/lab.py --host 127.0.0.1 --port 28183 --headless
```

Open `http://127.0.0.1:28183`. UI configuration defaults to live OpenAI model `gpt-5.4-mini` and API `http://127.0.0.1:4013`; select explicit labeled rehearsal with `SCHEDULING_MODE=rehearsal` before starting Marimo. `API_BASE` and `OPENAI_MODEL` configure the UI service/model; only standard `OPENAI_API_KEY` configures its live key. CLI fallback:

```sh
PYTHONPATH=src .venv/bin/python -m appointment_assistant --mode rehearsal --api-base http://127.0.0.1:4013
PYTHONPATH=src .venv/bin/python -m appointment_assistant --mode openai --api-base http://127.0.0.1:4013 --model gpt-5.4-mini
```

Restart mock to reset synthetic bookings/handoffs; use a new conversation to clear identity and consent. Reset does not resolve unknown prior effects. No runtime path may depend on ignored intake.

## Required checks and flows

Use the compatible virtual environment as PATH for the exact required suite:

```sh
PATH="$PWD/.venv/bin:$PATH" PYTHONPATH=src python3 -m unittest discover -s tests -v
```

After each modifying demo, restart the mock and start a fresh session. Repeat required flows in both CLI and Marimo; run live multi-turn qualification separately from rehearsal.

| Scenario / command suffix after `python -m appointment_assistant --mode rehearsal` | Expected observable result |
| --- | --- |
| `--demo provider_lookup` | Follow-up specialty/location turn; only returned providers; no patient identification |
| `--demo happy_path_booking` | Synthetic fixture identity, returned downtown primary-care options, selection then separate exact confirmation, exactly one matching scheduled appointment |
| `--demo no_patient_match` | Zero patient details/booking; correction then finite human next step; required failure demo |
| `--demo multiple_patient_matches` | Caller supplies ZIP privately; no candidate list; proceed only on unique match |
| `--demo appointment_lookup` | Verified patient only; appointments from supported GET |
| `--demo slot_conflict` | 409 explanation; fresh returned choice and consent required; no false success |
| `--demo handoff` | Real local POST; validated 201 says queued synthetic request, never human contact |
| `--demo api_failure --mock-scenario api_failure` | 503 on scheduling and handoff; explain neither booking nor queue succeeded |

Negative/boundary checks include selection-only/no/changed context/mixed yes/old yes, repeat confirmation/submission, invalid ordinal or extraction, empty slots, unsupported/medical requests, malformed booking 201, POST timeout and reactive exception replay. Unknown effects remain unknown and are not automatically retried. Verify actual API state/call counts, not only assistant text; use returned dates with fixed offset, not hard-coded calendar dates.

Inspect redacted proposed-action, guard, route-template, API outcome and latency evidence against [interaction](contracts/interaction.md); canary private values must be absent. Keep raw server logs out of exported evidence. Compare records through test-only private assertions, not evidence fields.

## Fresh-clone and handoff qualification

Mac ARM and Linux each need declared interpreter/Marimo versions, clean clone/copy identity and reviewed revision, install commands, test/demo outcomes, UI submit/edit/re-render behavior and measured feedback/completion duration. Report unavailable platform checks as pending; one host cannot prove both. Do not infer assignment-window compliance from these timings.

After integration, verify README setup/index and user recovery docs, actual-code architecture/walkthrough navigation/diagrams with date/revision, team exercise, short linked next steps and populated/deferred priorities. Update video notes with tested versus planned flows; an actual <=5-minute recording remains a later authorized delivery artifact. These local qualification checks do not themselves publish or submit anything. Approved private Git delivery is separate; public publication/submission and recording remain Operator-owned.
