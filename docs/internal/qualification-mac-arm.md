# Fresh-clone Mac ARM qualification

Updated: 2026-10-09 00:28 CDT. Qualified immutable source revision: `7e9f930b38cc58ea1e918be53baf01ba142b648d` (`main` as cloned). Later working changes or commits require affected-behavior qualification; these results do not automatically apply to later revisions.

## Environment and isolated clone

- Platform: `macOS-26.7-arm64-arm-64bit`, ARM64.
- Explicit bootstrap interpreter: `/Users/ken/codeRepos/DevOps/tmp/speckit-v110-audit.5nw5X1/venv/bin/python`, Python **3.11.13**.
- Task-owned clone: `/private/tmp/ochsner-lab-mac-20261009-bnmeb8/repo`.
- Source: authenticated normal SSH clone of approved private `git@kenerator-github.com:Kenerator/ochsner-scheduling-lab.git`.
- Fresh `.venv` created in clone; `.venv/bin/python -m pip install -e .` succeeded in **8.767 s** including environment creation. No global install or sibling source dependency used.
- Installed versions verified: `marimo==0.25.1`, `zen-engine==2.1.2`. `.venv/bin/python -m pip check` succeeded in **0.303 s**, reporting no broken requirements.
- Clone tracked/untracked status was clean after qualification. Temporary environment/artifacts are ignored or stored outside the clone. No live model credential was used; `OPENAI_API_KEY` was removed from test/demo/UI process environments.

## Tests and required demonstrations

From the fresh clone root, `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v` passed **90 tests** in **26.566 s** (26.691 s process wall time). This includes the actual supplied reference-server integration and real local ZEN decision tests. Live-interpreter tests use doubles; they do not establish a live model call.

Required aliases each succeeded with isolated reference state:

```bash
PYTHONPATH=src .venv/bin/python -m appointment_assistant --mode rehearsal --scenario success --json-summary
PYTHONPATH=src .venv/bin/python -m appointment_assistant --mode rehearsal --scenario failure --json-summary
```

Success process wall time: **0.565 s**. Failure process wall time: **0.565 s**. The failure path truthfully resolves to a queued synthetic handoff after unresolved identity; its `completed` outcome describes that handoff, not a booking or human contact.

All eight explicit rehearsal demonstrations also exited successfully. Each invocation creates and closes its own unchanged supplied mock server/store; no mutable booking state is shared with another candidate or demo.

| Demonstration/check | Exit | Process wall time | Terminal outcome |
| --- | --- | --- | --- |
| `provider_lookup` | 0 | 0.555 s | not_attempted |
| `happy_path_booking` | 0 | 0.558 s | completed |
| `no_patient_match` | 0 | 0.557 s | completed |
| `multiple_patient_matches` | 0 | 0.560 s | completed |
| `appointment_lookup` | 0 | 0.557 s | not_attempted |
| `slot_conflict` | 0 | 0.561 s | rejected |
| `handoff` | 0 | 0.559 s | completed |
| `api_failure` | 0 | 0.560 s | rejected |
| `marimo_check` | 0 | 1.143 s | static check passed |

The conflict demonstration terminates `rejected`; outage terminates `rejected` without falsely claiming the also-failing handoff queued. Appointment/provider lookup `not_attempted` denotes no write, rather than an unsuccessful read. These are deterministic rehearsal results, not genuine AI conversation evidence. See [live qualification](live-qualification.md) for separately recorded live work.

## Clean-clone UI qualification scope

`.venv/bin/marimo check apps/lab.py` passed with no diagnostics in **1.143 s**. A task-owned headless process started using:

```bash
SCHEDULING_MODE=rehearsal PYTHONPATH=src .venv/bin/marimo run apps/lab.py --host 127.0.0.1 --port 60059 --headless
```

The temporary loopback port was selected by an unused-port bind check before launch. HTTP root returned **200**, **18,041 bytes**, after **0.439 s**. Only the owned PID `56730` was terminated after the check. No unrelated occupant/process was killed. This establishes static validity and headless HTTP startup from the fresh clone, **not browser interaction, websocket cell execution, repeated-submit behavior, visual accessibility or full UI acceptance**. Main-task browser interaction qualification is separate.

## Evidence and reproduction

Local sanitized qualification artifacts remain in `/private/tmp/ochsner-lab-mac-20261009-bnmeb8/`: `install.log`, `pip_check.log`, `tests.log`, required-alias logs, `demo-*.log`, `marimo-check.log`, `marimo-startup.log`, `checks.json`, `demos.json`, and `startup.json`. Demo summaries contain only the approved nonidentity metadata projection; no live key or raw conversation was recorded. This temporary directory is evidence, not a runtime dependency or permanent archive guarantee.

[Reviewer README](../../README.md) · [Architecture](as-built/architecture.md) · [Code walkthrough](as-built/code-walkthrough.md) · [Native tasks](../../specs/001-appointment-assistant/tasks.md)
