# Development

Updated2026-10-09. [README](../../README.md) owns setup commands. Verify the chosen interpreter is3.11+, install locally with `pip install -e .`, and run `pip check`. Use the actual supplied server/data under vendor/reference-api; no ignored intake is required at runtime. Do not modify system Python or global tooling.

The reusable core is `src/appointment_assistant`; CLI and Marimo are thin adapters. OpenAI extraction carries only current text and normalized intent/field-presence/slot-count context. Deterministic Python validates records, identity, current options and literal consent; real ZEN consumes nonidentity boolean facts before effects. [Architecture](as-built/architecture.md), [walkthrough](as-built/code-walkthrough.md), [canonical tasks](../../specs/001-appointment-assistant/tasks.md).

Run `PATH="$PWD/.venv/bin:$PATH" PYTHONPATH=src python3 -m unittest discover -s tests -v`, then both required success/failure CLI demos from README. Tests create isolated real supplied HTTP servers. Live Responses doubles are explicitly simulated and distinct from [genuine qualification](live-qualification.md). Additional CLI demos cover duplicate ZIP, appointment lookup,409, human handoff and global outage.

## Team exercise

In a branch, change the wording of a clarification without changing authority. First add a behavior assertion that the new wording remains useful and exposes no candidate identity. Run conversation/UI tests, then full suite and booking/no-match demos. Review the exact-summary/consent boundary and evidence projection. Exercise is prepared, not claimed as performed by a team. A new specialty requires contract/fixture agreement; do not invent backend support.

Before committing run the [staged credential guard](security.md); retain existing hooks. No credentials in fixtures, logs or Git. [Review](reviews/adversarial-review.md) and [next steps](../product/next-steps.md) record limitations.
