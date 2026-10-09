# Implementation Plan: AI Appointment Scheduling Assistant

**Feature identifier returned by setup**: `001-appointment-assistant` | **Date**: 2026-10-08 | **Spec**: [spec.md](spec.md)

**Actual Git branch**: `main`; setup returns the feature identifier in its `BRANCH` field. No feature branch created; Git extension is not configured.

**Status**: Product implementation and synthetic qualification complete. Historical stage records remain below; [tasks and verification evidence](tasks.md) describe current outcomes. Actual video capture, named Persona validation and external delivery remain pending.

## Summary

Build a genuine multi-turn OpenAI text assistant with deterministic scheduling authority, a reusable Python core, thin Marimo Lab UI and CLI fallback. Provider facts, private patient verification, available slots, appointment lookup and confirmed bookings come only from the supplied local HTTP service. Selected synthetic handoffs report queued, failed and unknown outcomes truthfully. This plan incorporates the explicit developer answer; it does not convert intake or historical grants into broader execution permission.

## Technical Context

**Language/Version**: Python 3.11+; explicitly verify executable before setup/UAT.

**Primary Dependencies**: Standard library for core, `urllib` scheduling/Responses adapters and `unittest`; Marimo pinned to 0.25.1 for the selected UI; zen-engine==2.1.2 for a fixed proposed-action safety decision table. No OpenAI SDK or nxusKit dependency. Configurable model default `gpt-5.4-mini`; standard `OPENAI_API_KEY` environment only at authorized reviewer runtime. Missing credentials must give an actionable error in live mode, never silently simulate.

**Storage**: Session-scoped in-memory conversation, proposal, submission-generation reservations and sanitized event buffer. Supplied reference server owns in-memory synthetic appointments/handoffs. No durable or distributed idempotency.

**Testing**: Meaningful tests first: deterministic doubles, malformed extraction/HTTP boundaries, actual unchanged local mock integration and persona-placeholder acceptance cases. Required final command: `PYTHONPATH=src python3 -m unittest discover -s tests -v`; required provider/booking/no-match and failure demos; clean-clone Mac ARM and Linux setup/UI qualification. These were planned checks; current results are linked from [tasks.md](tasks.md).

**Target Platform**: Local Mac ARM and Linux, Python 3.11+, Marimo browser UI `127.0.0.1:28183`, scheduling mock `127.0.0.1:4013`. Network/model account needed only for explicitly selected live interpretation; labeled rehearsal remains credential-free.

**Project Type**: Reusable library with thin CLI and Marimo interface; supplied backend unchanged.

**Performance Goals**: Useful feedback around 400 ms where feasible, separate from model/effect completion. Measure scenario, environment, load and feedback/completion durations. Supplied 1.25-second extraction qualification does not establish product performance.

**Constraints**: Synthetic fixtures; no invented backend/clinical rules, no raw sensitive evidence, no model-authorized effects, no automatic unknown POST retry. Reserve submission before effects. Approved internal UI assets only; public redistribution remains outside their grant. Historical Plan execution performed no credential access, live calls, publication or deployment. Current Implement work uses only separately approved local/live and private-destination grants.

**Scale/Scope**: One session, sequential effects; Stories 1–6 / FR-001–018 plus explicitly selected private ZIP, appointment lookup, recorded synthetic handoff and Marimo evidence UI. Marimo is selected across four candidates; this native feature owns only Lab. Reschedule/cancel, production identity/security, durable replay protection and live human delivery remain outside scope. Video recording/submission remains separately authorized delivery work.

## Constitution Check

Against Constitution 0.2.1; pre-research and post-design checks both PASS without exceptions:

| Principle | Pre-research commitment | Post-design assessment |
| --- | --- | --- |
| I Empathy | Retain primary-user, Support/Admin and reviewer placeholders | Spec mappings preserved; private ZIP and finite recovery; no invented Persona validation |
| II Predictable interaction | Explicit exact current consent; distinct outcomes | Deterministic current whole-message yes/confirm after summary; context invalidation; unknown-effect reconciliation; no reactive replay |
| III Responsiveness | Separate feedback/completion measurement | Event timing contract; no unmeasured SLA or time-window claim |
| IV Small core | Thin adapters, credential-free rehearsal | Core owns permissions/state; Responses proposes extraction only; Marimo/CLI render and submit |
| V Verification | Tests before behavior; real local fixtures; clean setup | Tasks handoff below requires meaningful boundary/integration tests, demos and Mac ARM/Linux qualification |
| VI Truthful exploration | Synthetic data, no secrets or live-delivery claims | Fixed evidence whitelist; queued synthetic handoff only on validated 201; no stage execution permission expansion |
| VII Documentation | As-built after stable code/integration | Near-final code/test walkthrough and architecture, revision/date/navigation/diagrams, team exercise and truthful video notes |
| VIII Governance | Single authorities, safe parallel ownership | Read-only research parallel; future disjoint tests/code ownership with native P dependencies; native state main-owned |

**Gate result**: No unresolved planning clarification or justified violation. Constitution, bootstrap controls and managed assets unchanged. [Research](research.md) records selection, alternatives and evidence limits.

## Project Structure

### Feature documentation

```text
specs/001-appointment-assistant/
├── spec.md                       # Read-only prerequisite
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   ├── interpretation.schema.json
│   ├── scheduling.md
│   └── interaction.md
├── quickstart.md
├── checklists/requirements.md    # Existing
└── tasks.md                      # Generated after Plan; current implementation authority
```

### Historical planned source layout (see current as-built documentation)

```text
src/appointment_assistant/
├── models.py                    # Records and outcomes
├── conversation.py              # Deterministic identity/proposal/consent
├── interpretation.py            # Extraction interface and labeled rehearsal
├── openai_interpreter.py         # urllib Responses extraction
├── scheduling.py                # Validated scheduling HTTP boundary
├── events.py                    # Standalone sanitized emitter
├── submission.py                # Reserve-before-effects generation gate
├── policy.py                    # Real ZEN proposed-action safety gate
├── ui_adapter.py                # Explicit form submission/evidence boundary
└── __main__.py                  # CLI/run/demo configuration
apps/lab.py                      # Thin Marimo 0.25.1 explicit-submit form UI
rules/safety.json                # Fixed nonidentity ZEN policy
vendor/reference-api/
├── mock-api/server.py            # Unchanged supplied source
├── data/*.json                   # Four unchanged synthetic fixtures
└── openapi/scheduling-api.yaml   # Unchanged supplied contract
licenses/                        # MIT pattern license when adopted
tests/
├── test_conversation.py
├── test_interpretation.py
├── test_scheduling.py
├── test_events.py
├── test_submission.py
├── test_policy.py
├── test_lab_ui.py
└── test_acceptance.py            # Pending acceptance task; not a delivered-file claim
```

**Structure Decision**: Do not modify managed `poc_template` machinery to implement the product. Keep `poc_demo` starter distinct from feature demonstrations. Approved `assets/ui/` logo/theme applied by UI only. Selective vendor manifest/hashes and license/provenance are implementation work; ignored RFP is planning source, not runtime dependency.

## Design and selected scope reconciliation

Historical starter decisions described a generic one-operation synthetic demonstration. The current [Lab decisions](../../docs/product/decisions.md) replace that execution design with service-derived facts and genuine AI extraction while retaining reusable core/effect boundaries. Cached submission/proposal results prevent repeat invocation only within one session. No production security or distributed guarantee is inferred.

The prerequisite spec labels GUI, appointment lookup and recorded handoff as optional candidates; the explicit developer answer now selects them for implementation. Required safety policies remain unchanged. Selection is recorded here and in contracts, without re-running Specify/Clarify or rewriting the prerequisite. Named Personas remain unresolved as the native spec already allows.

See [data model](data-model.md), [scheduling contract](contracts/scheduling.md), [interaction contract](contracts/interaction.md) and [extraction schema](contracts/interpretation.schema.json). Model has no patientId/slotId/confirmed/action authority fields. Deterministic code renders facts and checks the literal current message independently of model output.

## Historical Plan-to-Tasks handoff

The following was the Plan-stage handoff used to generate [tasks.md](tasks.md); the product implementation is now qualified. The historical instruction was to generate native tests-first tasks with requirement/story links and these dependencies:

- Foundation: selectively vendor unchanged reference artifacts with sibling layout/provenance; add declared UI dependency/configuration, licensing and model schema. Preserve synthetic fixtures and hooks/configuration.
- Disjoint test owners may work in parallel once contracts are stable: scheduling tests then adapter; extraction tests then interpreter; event/submission tests then standalone patterns. Each pair retains tests-first order and exclusive files; main integrates contracts/native state.
- Core tests then workflow implementation depend on validated model/HTTP contracts. Cover public lookup, private ZIP ambiguity/no-match, verified appointment lookup, current proposal invalidation, selection without consent, decline, exact consent, repeat submission/confirmation, conflict, timeout/invalid 201 unknown and truthful 201/503 handoff.
- CLI and Marimo tasks depend on stable core/submission gate. The selected UI uses `text_area.form` with an explicit Send callback and read-only transcript/evidence; this avoids the reproduced Marimo 0.25.1 chat RPC metadata mismatch without changing the pin. Redacted evidence/branding UI tests include reactive replay, exceptions, changed fields, repeated text as distinct submissions and no raw sensitive event fields. Live synthetic multi-turn model qualification is distinct from credential-free rehearsal.
- Required integrations and success/failure demos before near-final documentation. Independent as-built architecture and walkthrough sections may be drafted in parallel once their actual code/tests stabilize; main owns final integration and verifies revision/date/navigation/diagrams.
- Final README clean setup/index, team exercise, video notes, short linked next steps and populated or explicitly deferred backlog/roadmap/sprint planning. Qualify fresh-clone Mac ARM and Linux, reporting unavailable environments honestly. Run required unittest command and demos; avoid claims based on stubs or simulator-only runs.
- Consider one optional independent adversarial review and optional post-MVP UI refinement with documented pre/post milestones; neither blocks required implementation. Commit/tag/credential guard and any destination grants follow project policy at their authorized stage. No automatic push/public delivery.

## Complexity Tracking

No constitutional violations requiring justification. Reserve-before-effects submission generation is deliberately session-only; unknown booking outcome remains a reconciliation boundary.

## Stage Handoff

Native setup continued the contracted directory; pre/post hook checks found no `.specify/extensions.yml`. Phase 0 research and Phase 1 design are complete. At the historical Plan handoff, Tasks was next and Plan ended at Phase 1. Tasks, all-severity Analyze remediation and product implementation have since completed. Clean-clone Mac ARM and Linux qualification is recorded in [tasks.md](tasks.md); actual video capture remains pending.

## Lab action policy refinement — 2026-10-08

Use src/appointment_assistant/policy.py and rules/safety.json, backed by actual ZEN 2.1.2. Closed boolean facts, no identifiers/free text or external loaders. Decisions have allowed:boolean and fixed code. Public provider/patient search and safe handoff are allowed; availability/appointment lookup require verified identity; booking requires verified identity, a current API slot and current literal bound consent with no unknown prior write. Unknown or invalid operation/facts/engine result fails closed. Conversation consumes verdict before effects while retaining independent transaction guards. Medical/unsupported requests stop scheduling and use truthful human handoff. tests/test_policy.py exercises real decisions and engine failure; integration tests prove denied actions have zero effects. ZEN is a Lab validator, not clinical eligibility, production authorization or durable idempotency.
