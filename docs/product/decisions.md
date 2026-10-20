# Lab decisions

Updated: 2026-10-08.

- Genuine OpenAI structured extraction (configurable gpt-5.4-mini) proposes intent/field patches/ordinal only; no factual or clinical prose is trusted. Rehearsal is explicitly labeled.
- Deterministic session code owns private identity, current API options, exact consent and effects. Booking and handoff success require validated HTTP 201; successful read operations require validated HTTP 200; unknown POST outcome cannot be retried blindly.
- ZEN2.1.2 provides a real fail-closed proposed-action safety gate over nonidentity boolean facts. No clinical/eligibility rules are invented.
- Lab adapts attributed public standalone event/submission patterns; no nxusKit runtime. Redacted evidence is constructed from a whitelist, not copied raw payloads.
- Supplied reference API/data are unchanged selective private reviewer assets. Each process/test owns isolated booking state.
- Marimo0.25.1 on loopback28183 and CLI share the core; submitted generations are reserved before effects. This is session replay protection, not durable API idempotency.
- Private Kenerator/ochsner-scheduling-lab delivery is approved; public submission remains Operator-owned. Budget compliance and Persona validation are not asserted.

See [native plan](../../specs/001-appointment-assistant/plan.md) and [tasks](../../specs/001-appointment-assistant/tasks.md).

## Credential policy — 2026-10-20

Until further notice Ochsner-supplied-key use is paused. Normal Lab launch explicitly selects our own Secure Note `[Env] OPENAI_API_KEY`, notes field, through the existing trusted helper. This replaces the previous item selection; it is not fallback after failure and cannot use an inherited/stale key. Model defaults/overrides and all effect/accounting protections remain unchanged. No new paid qualification, relaunch or scheduling effect is authorized by this change. Historical evidence remains source/account-bound.
