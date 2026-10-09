# Linux clean-clone qualification

Updated: 2026-10-09. Reviewed source revision: `7e9f930b38cc58ea1e918be53baf01ba142b648d` (`main`). The qualification clone had empty `git status --porcelain` after checks. This report is a subsequent documentation change and is not part of that reviewed revision.

A fresh authenticated clone of the approved private origin was created on `x360-Minty` at `/tmp/ochsner-lab-linux-20261009-s5wed0v3/repo`. Platform: Linux x86_64, kernel `7.0.0-34-generic`, glibc2.39; explicit interpreter `python3.12`, version3.12.3. No existing environment was copied, no global packages installed, and no OpenAI credential was copied. Rehearsal commands removed `OPENAI_API_KEY` from their process environment.

## Performed checks

From the clean clone, `python3.12 -m venv .venv`, `.venv/bin/python -m pip install -e .` and `.venv/bin/python -m pip check` succeeded. Editable installation took13.715seconds; dependency checking took0.542seconds. Installed Marimo0.25.1 and zen-engine2.1.2 matched the declared pins.

`PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v` passed **90 tests in28.257seconds** (28.537seconds process wall time). This exercised real supplied mock stores, adapter/core failures, privacy evidence, submission replay and UI adapter tests. Responses-shaped model doubles remain doubles; the suite does not establish live model access on Linux.

Both CLI aliases passed: `--mode rehearsal --scenario success --json-summary` ended `booked/completed`; `--scenario failure` ended `handoff/completed`, meaning a request queued in the synthetic service. Each command created its own fresh supplied mock.

All eight named CLI demonstrations passed in explicitly selected rehearsal mode:

| Demo | Terminal state / outcome | Process wall time |
| --- | --- | --- |
| `provider_lookup` | providers / not_attempted | 0.658s |
| `happy_path_booking` | booked / completed | 0.640s |
| `no_patient_match` | handoff / completed | 0.637s |
| `multiple_patient_matches` | booked / completed | 0.666s |
| `appointment_lookup` | appointments / not_attempted | 0.623s |
| `slot_conflict` | conflict / rejected | 0.631s |
| `handoff` | handoff / completed | 0.620s |
| `api_failure` | handoff / rejected | 0.629s |

`not_attempted` is the core's consequential-effect outcome label; successful read operations are separately visible in API evidence. Handoff completion means mock storage only, never confirmed human contact. These command timings include process/mock lifecycle and are not interaction-response or400ms feedback claims. No raw patient transcripts, model prompts or upstream audit were exported.

`.venv/bin/marimo check apps/lab.py` exited0. Headless Marimo on a task-owned unused loopback port returned HTTP200 after1.086seconds; its separately owned mock and UI processes were then stopped. HTTP startup is not a browser interaction test.

## Browser qualification status

At report creation, a separate task-owned rehearsal UI was started on Linux loopback28185 with a fresh supplied mock on loopback4015 for the parent task's controlled browser qualification. Startup returned HTTP200. Only this task's recorded processes are eligible for cleanup; other services were untouched. Browser submission, editing, rerender, confirmation and reset interaction remain **pending** until observed and recorded by the parent task. Linux live OpenAI qualification is unperformed; no credential transfer was needed for these checks.

Task-local machine evidence is retained outside the repository in `/tmp/ochsner-lab-linux-20261009-s5wed0v3/qualification.json`. The temporary checkout and environment are qualification artifacts, not a deployment.

See [setup](../../README.md), [demo runbook](demo.md), [live qualification](live-qualification.md) and [canonical task progress](../../specs/001-appointment-assistant/tasks.md).

## Controlled IAB interaction — 2026-10-09 00:37CDT

Parent forwarded only owned loopback28185 through established SSH. Clean-clone rehearsal UI visibly passed provider lookup, verified API options, separate selection then literal yes→scheduled booking, reset warning, no-match without candidate disclosure and actual mock queued handoff/nohumancontact statement. No Linux livekey/model call. Early browser helper targeted its captured original tab; explicit target binding resolved test-control error, no application change. UI/API remain owned for final review until explicitly stopped.

## Exact persona candidate follow-on — 2026-10-09 01:36:13 CDT

Existing isolated clone was clean before checkout and after qualification at `66adbf54eb22020eb505f611f9545451b9888dfa`. Python3.12.3; no credentials or dependency changes. All95 tests passed in30.829 seconds; success alias completed/booked (39.1ms), failure alias completed/queued mock handoff (32.8ms); Marimo check passed. No persistent server/UI launched. This follow-on reuses the installed clean-clone environment; the original fresh-install evidence above remains bound to its original revision.
