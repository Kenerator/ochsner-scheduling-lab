# Persona, story and test index

Updated: 2026-10-12. Launcher candidate baseline `1726469`; runtime manifest source `b7875452e3a999ca69ce170822c66e7f679b4442`. Exact Persona pins and hypothesis limits remain in [Personas](../product/personas.md); this update adds no validation or permissions.

| Pinned Persona constraint | Native story and design/code | Relevant evidence and limits |
| --- | --- | --- |
| Sam-Rae AGENT QA: reproducible setup and visible mode | [Story6/FR018](../../specs/001-appointment-assistant/spec.md), `poc-launch.json`, installed launcher | `tests/test_runtime_launcher.py`: actual CLI/UI constructors with fake transport, default/env/explicit model routing, manifest hashes, explicit rehearsal, no-call help/doctor. Not live-model or new browser qualification. |
| Morgan-Rae: safe diagnostic and recovery context | [Stories5–6](../../specs/001-appointment-assistant/spec.md), launcher role environments/errors/cleanup | Launcher tests preserve foreign listeners, remove model/vault secrets from mock environment, clean owned offline CLI/API; existing support-summary tests and historical [live evidence](live-qualification.md) retain their original scope. |
| Jules and Ellie-Rae: predictable scheduling/confirmation and accessible recovery | [Stories1–4](../../specs/001-appointment-assistant/spec.md), unchanged core/UI | Existing conversation/acceptance/UI tests and historical live evidence; new launch routing tests do not prove new browser/keyboard behavior or validate Persona hypotheses. No scheduling/UI behavior change in this delta. |

Candidate test results, review and integration revision remain authoritative in [native tasks](../../specs/001-appointment-assistant/tasks.md). Production/admin-console coverage is outside this launch-only delta, with existing [next steps](../product/next-steps.md) retained.
