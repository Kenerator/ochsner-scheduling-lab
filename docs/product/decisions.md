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
