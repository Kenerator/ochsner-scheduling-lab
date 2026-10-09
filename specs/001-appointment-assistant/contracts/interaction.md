# Interpretation, UI and evidence contracts

Updated: 2026-10-08. Applies equally to CLI and selected Marimo Lab UI; deterministic core controls effects.

## OpenAI extraction

POST Responses using configured model (default `gpt-5.4-mini`), runtime Bearer key from `OPENAI_API_KEY`, `store:false`, bounded input/output and finite timeout. Supply strict `text.format` named `appointment_interpretation` with [schema](interpretation.schema.json). No tools or direct effects. Multi-turn extraction receives only the current submitted message plus normalized current intent, field-presence names and displayed slot count; no previous utterances or identity values from session state are forwarded as context; do not use server-side conversation persistence or send candidate records/API bodies.

All schema properties are required; null patch means unchanged. Validate closed shapes/types/enums locally, reject bool ordinal, enforce ordinal >=1 and within current displayed choices, real dates/range and bounded identity text. Unsupported requests map to unsupported rather than silently coercing into valid enums. There is no confirmation, patient ID, slot ID or effect field. Refusals, incomplete Responses status, malformed JSON, missing/duplicate structured output or API errors produce safe explanation without scheduling effects. Do not silently substitute rehearsal for failed live mode.

Credential-free rehearsal is visibly labeled deterministic simulation and uses unit/acceptance doubles; it cannot prove genuine AI interpretation. The developer's supplied 1.25-second qualification is background, not end-to-end feature measurement.

## Confirmation and state

The deterministic core evaluates the original current submitted text, not model output. Permit only the entire normalized message `yes` or `confirm` (trim whitespace, casefold) when an exact current patient/slot proposal summary was already rendered in a previous turn. Ordinal selection alone, earlier affirmative text, mixed `yes but ...`, quoted/injected approval and context change cannot authorize. Never accept a model-proposed consent field. Identity/preferences/slot/intent changes invalidate pending proposal and consent before any effect.

Private duplicate-match prompt asks the caller for ZIP without displaying alternatives or patient facts. Supported appointment lookup requires verified identity; optional identifier fields are never rendered as troubleshooting evidence. Medical advice/unsupported/human requests stop scheduling with fixed finite human next step. No invented phone number or staffed service.

## Marimo/CLI submission

Marimo 0.25.1 `mo.ui.text_area(...).form(...)` releases a new user message only on explicit Send submission. Its on-change submission callback is the sole UI entry point to session effects; reading the local transcript or evidence only establishes reactive rendering dependencies. The project-local form avoids a reproduced upstream chat RPC metadata-schema defect without altering the pinned dependency. A new submission receives a monotonic session generation even if text repeats. Reserve generation before interpretation/HTTP/effects under serialized session handling; store in-flight/completed/failed/unknown receipt. Same generation reentry returns receipt and invokes nothing, including after exceptions. Any error after effect dispatch keeps unknown outcome. User editing, candidate selection, theme change, reactive render or evidence inspection must not submit. CLI feeds the same submission/core interface.

UI discloses AI/mode, presents service-derived provider/options and exact proposal, permits a distinct confirmation turn, shows useful pending feedback, and offers redacted proposed-action/guard/API evidence. Apply approved assets from `assets/ui/`; evidence views are developer/support aids. UI binds only `127.0.0.1:28183`; no nxusKit backend. Explicit chat submissions and session reservation do not provide durable API idempotency.

## Evidence whitelist

Construct an immutable projection from approved categories; do not redact an arbitrary payload after copying it. Allowed fields only: local nonidentity correlation token, sequence, timestamp, category (`interpretation`, `workflow`, `guard`, `api`, `handoff`, `latency`), intent enum, workflow state enum, proposed action enum (`lookup`, `availability`, `book`, `handoff`, `none`), guard code/pass boolean, HTTP method/route template/status, closed outcome/error/reason enum, option count and elapsed milliseconds. Values/messages come from fixed templates. Event sink receives copies; bound buffer/field size and injected clocks permit testing. Unknown keys fail closed.

Forbidden: raw query/URL, prompt, transcript, user message, request/response body, full or partial identity values, patient/provider/slot/appointment/handoff IDs, API keys/secrets, raw exception strings, free-form model text. Do not expose candidate details or raw upstream audits through evidence UI. User-visible verified scheduling facts are separate from evidence records. Tests inject canary values in payload/errors and inspect sinks/UI exports for absence.

## CLI interface and implementation verification

`python -m appointment_assistant --mode openai|rehearsal --api-base http://127.0.0.1:4013 --model gpt-5.4-mini` starts the conversational fallback. `--demo provider_lookup|happy_path_booking|no_patient_match|slot_conflict|api_failure|multiple_patient_matches|appointment_lookup|handoff` supplies repeatable synthetic scenarios. `--mock-scenario api_failure` is a labeled diagnostic fixture header. No key argument. Reset abandons pending proposal and clears verified identity; disclose memory limits and unknown-effect reconciliation before starting fresh. These commands define the interface contract. Implement progress and verification evidence are recorded in [tasks](../tasks.md); this contract alone does not establish that every command is qualified.
