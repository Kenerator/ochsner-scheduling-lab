# Planning research

Updated: 2026-10-08. Read-only inspection and official documentation; no application or live-model execution in this stage.

## AI interpretation

- Decision: Use Python standard-library `urllib.request` to call `POST https://api.openai.com/v1/responses`, configurable model default `gpt-5.4-mini`, with strict `text.format` JSON Schema. Read `OPENAI_API_KEY` only from the reviewer runtime environment. Keep labeled credential-free rehearsal and unit doubles.
- Rationale: The explicit developer answer selects genuine multi-turn interpretation without an SDK. Official [model documentation](https://developers.openai.com/api/docs/models/gpt-5.4-mini) lists Responses and structured-output support. The [Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs) documents strict schema extraction, nullable required properties, closed objects and refusals. Parse response output message content; refusal, incomplete output and invalid extraction stop safely. Local validation remains mandatory.
- Alternatives considered: Local model and simulator-only paths were not selected; SDK adds an unnecessary dependency. Direct model tool execution would cross the approved authority boundary.
- Evidence limit: Developer reports a completed structured call in 1.25 seconds. This is supplied qualification evidence, not a measurement reproduced here or an application latency claim. Multi-turn product qualification remains implementation work.

## Scheduling boundary

- Decision: Use only the six routes in the supplied OpenAPI/server. Selectively vendor unchanged server, four JSON fixtures and OpenAPI under `vendor/reference-api/`, preserving sibling `mock-api`, `data`, `openapi` layout. Explicitly run port 4013.
- Rationale: A clean clone cannot rely on ignored intake. Source inspected at `docs/product/RFP/source/openapi/scheduling-api.yaml` and `mock-api/server.py`. The server resolves data relative to its own path; restart resets in-memory bookings. Its default 4010 is overridden, without changing the server.
- Alternatives considered: Runtime intake dependency, invented endpoints and replacement backend rejected. Vendoring happens in implementation, not Plan.
- Findings: Schemas omit required response fields and server validation is permissive. Client validates envelopes, booleans, enums, IDs and calendar dates. Slots contain provider IDs, so names join returned providers. Appointment response omits slot ID: validate patient, provider, specialty, location, time and scheduled status against the proposal. No idempotency key or proposal status endpoint exists. Timeout/invalid POST success is unknown; never replay automatically. `409` requires fresh search, choice and consent. No clinical or established-patient restrictions are implemented; do not invent them.

## Identity and selected extensions

- Decision: Implement appointment lookup after unique verification and real local `POST /handoffs`. Ask for ZIP privately when phone/DOB returns multiple matches; compare internally, revealing no candidate identities/ZIPs. Use deterministic handoff reason and summary templates.
- Rationale: These are expressly selected useful extensions, using supported routes. Public providers require no identity. Fixed timezone offset and server-relative dates remain disclosed limitations.
- Alternatives considered: Displaying candidate identifiers or adding ZIP API parameters rejected; ZIP is a local discriminator. Live human delivery is not selected. Global `api_failure` returns 503 even on handoffs; only validated 201 proves queued synthetic receipt.

## Marimo and standalone Lab patterns

- Decision: Marimo 0.25.1 is the selected thin UI for all four candidates; this feature implements the Lab lane at loopback 28183 with CLI fallback, without building the other candidate repos. Use explicit submission generations and reserve each generation before interpretation/effects. Retain in-flight/completed/failed results to prevent reactive replay.
- Rationale: The developer selected standalone event-emitter/submission-gate patterns from public `nxus-SYSTEMS/nxusKit-examples` revision `fd801bbc548e88fb5858e924089f3753fe7b0650`. Adapt only relevant patterns, no nxusKit dependency. Preserve MIT attribution/license in `THIRD-PARTY-NOTICES.md` and licenses when code is adopted. Upstream generation gate marks completion after execution; reservation before effects is a required strengthening.
- Alternatives considered: Auto-executing effects from reactive cell changes, optional UI-only selection and adopting nxusKit runtime rejected. Session gate is not durable API idempotency.
- Evidence privacy: Event schema validation alone cannot sanitize free text. Construct fixed allowlisted events and UI evidence projections; never project raw query, prompt, transcript, body, identity or secrets. Upstream server audit includes a patient ID in lookup paths and must not be imported as redacted application evidence.

## Resolution and research ownership

The explicit `ai_execution_path` answer resolves the previous planning question. Scheduling and Marimo/pattern research ran independently with read-only owners; the main session owns native files. No unresolved technical choice or constitutional exception remains. Named primary-user, Support/Admin and reviewer Personas remain explicit placeholders in the spec, with selection/validation as a next step rather than invented research.

## Pinned UI/source references

Read-only source verification confirms `.form()` explicit submission and `on_change`, plus host/port/headless CLI options in [Marimo 0.25.1 input source](https://github.com/marimo-team/marimo/blob/0.25.1/marimo/_plugins/ui/_impl/input.py) and [CLI source](https://github.com/marimo-team/marimo/blob/0.25.1/marimo/_cli/cli.py). See [forms](https://docs.marimo.io/api/inputs/form/) and [reactivity](https://docs.marimo.io/guides/reactivity/). A session gate is a design inference from reactive reruns, not a Marimo idempotency guarantee.

Selected upstream [run_events.py](https://github.com/nxus-SYSTEMS/nxusKit-examples/blob/fd801bbc548e88fb5858e924089f3753fe7b0650/examples/integrations/common-sense-guardrails/python/run_events.py) and [frontend_core.py](https://github.com/nxus-SYSTEMS/nxusKit-examples/blob/fd801bbc548e88fb5858e924089f3753fe7b0650/examples/integrations/common-sense-guardrails/marimo/frontend_core.py) are confirmed at the pinned revision. The repository offers [dual licensing](https://github.com/nxus-SYSTEMS/nxusKit-examples/blob/fd801bbc548e88fb5858e924089f3753fe7b0650/LICENSE); select and retain the [MIT notice](https://github.com/nxus-SYSTEMS/nxusKit-examples/blob/fd801bbc548e88fb5858e924089f3753fe7b0650/LICENSE-MIT). Installation, browser behavior and fresh-clone execution are not qualified during Plan.
