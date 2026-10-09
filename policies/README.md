# Adopted action policy

Updated2026-10-09. Lab uses a real fixed ZEN2.1.2 proposed-action decision table at [rules/safety.json](../rules/safety.json), consumed by [PolicyGate](../src/appointment_assistant/policy.py). Source: approved FR-018 and [plan refinement](../specs/001-appointment-assistant/plan.md#lab-action-policy-refinement--2026-10-08), grounded in supplied scheduling/confirmation/privacy policies. No clinical or eligibility rules are invented.

Closed boolean facts describe verified identity, current slot, current literal consent and prior unknown write. Public lookup/search and safe handoff are allowed; patient reads require verified identity; booking requires all current facts and no unknown write. Malformed input/engine output fails closed. The deterministic Session independently binds patient/options/consent before adapter effects. A rule verdict does not prove consent or external completion.

[Real-engine tests](../tests/test_policy.py) and [workflow denial/no-effect tests](../tests/test_conversation.py) qualify this synthetic boundary. No other engine is selected. Generic subdirectories are retained extension references, not installed or adopted policies. [Native tasks](../specs/001-appointment-assistant/tasks.md) own progress.
