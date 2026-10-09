# Ochsner Scheduling Lab

A local, synthetic appointment assistant for private review. OpenAI extracts requests; deterministic Python and a real ZEN safety table control effects. The unchanged supplied scheduling API supplies every provider, patient, slot and appointment fact. The Marimo UI shows conversation beside nonidentity evidence.

## Setup

Supported reviewer platforms: **Mac ARM and Linux x86_64**, Python **3.11+** (verify with `python3.11 --version`). Private repository access must already be authorized/authenticated; standard SSH `git@github.com:Kenerator/ochsner-scheduling-lab.git` is also supported. The maintainer-specific `kenerator-github.com` alias is optional local configuration, not a reviewer prerequisite. From a fresh authenticated clone of the approved private repository:

```sh
git clone https://github.com/Kenerator/ochsner-scheduling-lab.git
cd ochsner-scheduling-lab
python3.11 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m pip check
```

On Linux, a verified Python3.12 executable is also supported. Dependencies are pinned in `pyproject.toml`: Marimo0.25.1 and ZEN2.1.2. No nxusKit/OpenAI SDK is required. Live mode defaults to `gpt-5.4-mini`; optional `OPENAI_MODEL` selects an authorized compatible model, `API_BASE` selects the local scheduling API, and `SCHEDULING_MODE` is `openai` or `rehearsal`. CLI exposes `--model` and `--api-base` too. Live mode needs `OPENAI_API_KEY` securely supplied in the process environment; never paste it in chat, source or CLI arguments. Missing credentials fail visibly. `--mode rehearsal` explicitly selects deterministic simulation.

## Run

Terminal1 starts the supplied synthetic API. Its raw audit includes patient route identifiers, so discard it rather than exporting it as Lab evidence:

```sh
.venv/bin/python vendor/reference-api/mock-api/server.py --port 4013 > /dev/null
```

Terminal2 starts the UI without launching an external browser:

```sh
PYTHONPATH=src .venv/bin/marimo run apps/lab.py --host 127.0.0.1 --port 28183 --headless
```

Open `http://127.0.0.1:28183` in the controlled in-app browser. To rehearse without credentials, prefix the UI command with `SCHEDULING_MODE=rehearsal`. CLI fallback:

```sh
PYTHONPATH=src .venv/bin/python -m appointment_assistant --mode rehearsal
```

Ask to book primary care downtown; supply synthetic phone `555-0101` and DOB `1985-04-12` when asked. Choose an API option, review the exact summary, then send **yes** or **confirm** separately. Selection alone never books. Provider lookup is public; appointment lookup requires verified synthetic identity. Never use real patient data.

## Verify and reset

```sh
PATH="$PWD/.venv/bin:$PATH" PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python -m appointment_assistant --mode rehearsal --scenario success
PYTHONPATH=src .venv/bin/python -m appointment_assistant --mode rehearsal --scenario failure
PYTHONPATH=src .venv/bin/python -m appointment_assistant --mode rehearsal --demo api_failure --json-summary
```

Each CLI demo owns a fresh supplied mock and in-memory state. `reset` clears conversation only; restart **your own** API process to restore fixtures and open a fresh UI session. Unknown booking/handoff outcomes require human reconciliation; reset cannot prove failure. Generation reservations prevent reactive replay only within a session, with no durable/distributed idempotency.

## Documents

- [Specification](specs/001-appointment-assistant/spec.md), [plan](specs/001-appointment-assistant/plan.md), [canonical task progress](specs/001-appointment-assistant/tasks.md)
- [User setup](docs/user/getting-started.md), [recovery](docs/user/recovery.md), [developer setup and exercise](docs/internal/development.md)
- [Demo runbook](docs/internal/demo.md), [live qualification](docs/internal/live-qualification.md), [video notes](docs/internal/video-notes.md)
- [Architecture](docs/internal/as-built/architecture.md), [code walkthrough](docs/internal/as-built/code-walkthrough.md), [decisions](docs/product/decisions.md)
- [Stories](docs/product/user-stories.md), [personas](docs/product/personas.md), [backlog](docs/product/backlog.md), [roadmap](docs/product/roadmap.md), [work increments](docs/product/sprint-planning.md), [next steps](docs/product/next-steps.md)
- [Asset rights](docs/internal/ui-assets.md), [third-party notices](THIRD-PARTY-NOTICES.md), [credential guard](docs/internal/security.md), [review](docs/internal/reviews/adversarial-review.md), [milestones](docs/internal/milestones.md)

This is fixture verification, not production authentication or medical/clinical eligibility. No medical advice, cancellation, rescheduling or confirmed human delivery. A validated handoff201 means queued in the mock. Fixed fixture times use −05:00. Private reviewer assets do not grant public redistribution. Persona validation, production controls and video recording/submission remain separate work.
