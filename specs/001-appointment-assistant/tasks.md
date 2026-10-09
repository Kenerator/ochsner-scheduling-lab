# Tasks: AI Appointment Scheduling Assistant

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [contracts](contracts/interaction.md), [quickstart.md](quickstart.md).
**Updated**: 2026-10-09. Implement in progress after cumulative Specify, Plan, Tasks and Analyze stages. Checkboxes remain pending until the main owner reconciles observed implementation, tests, demos and qualification evidence; document corrections do not mark work complete.
**Tests**: Required by the developer and Constitution. Write meaningful tests, run and observe the intended behavioral failures before implementing each dependent behavior; run them again after implementation. Existing passing tests are not a substitute for new behavior tests.
**Organization**: Setup → foundation → six native stories in priority order → final integration/documentation. Selected extensions in Plan are accepted scope, despite prerequisite Spec's historical optional labels. Primary-user, Support/Admin and reviewer Personas remain explicit unresolved placeholders; do not invent validation or permissions.

## Format and path conventions

Every actionable item uses `- [ ] Tnnn [P?] [USn?] Description with file path`. Paths are repository-relative. `[P]` means eligible for concurrent execution only after listed prerequisites pass, with disjoint files and one owner per file. Main owns `tasks.md`, shared integration files and native state. No competing Spec-Kit stages, bootstrap/managed-asset/Constitution changes, automatic pushes or publication. Historical Tasks generation performed no credential or model access. Current Implement live qualification is separately approved; no artifact grants additional access or publication authority.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Declare a project-local runtime and preserve the unchanged supplied service and pattern provenance.

- [x] T001 Verify an explicit Python 3.11+ executable, inspect existing packaging/hooks, and declare editable `src/` package plus `marimo==0.25.1` and `zen-engine==2.1.2` in `pyproject.toml`; document project-local environment commands in `docs/internal/development.md` without altering managed tooling or global configuration.
- [x] T002 [P] Selectively copy unchanged `docs/product/RFP/source/mock-api/server.py`, four `data/*.json` fixtures and `openapi/scheduling-api.yaml` to sibling directories under `vendor/reference-api/`; record source paths and byte hashes in `vendor/reference-api/manifest.json`, retain fixtures and verify equality; runtime must not depend on ignored RFP.
- [x] T003 [P] Retain the MIT notice for adapted `run_events.py` and `marimo/frontend_core.py` patterns from public revision `fd801bbc548e88fb5858e924089f3753fe7b0650` in `licenses/nxusKit-examples-MIT.txt` and `THIRD-PARTY-NOTICES.md`; record exact upstream paths/adaptation scope without adding nxusKit dependency or implying UI redistribution rights.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish validated records, interpretation/HTTP boundaries, privacy-safe events and reserve-before-effects submission handling. All story implementation depends on this phase. Tests-first pairs below may run as independent owned lanes once Setup is complete.

- [x] T004 [P] Write failing closed-record validation tests in `tests/test_models.py` for constraints quoted in T010, malformed/mismatched entities, bool-as-integer, timezone/date range, required arrays and unknown keys; use private synthetic assertions rather than exporting identities.
- [x] T005 [P] Write failing six-route contract tests in `tests/test_scheduling.py` for `contracts/scheduling.md`: URL encoding, finite timeout/bounds, invalid input before I/O, response validation, 201 exact appointment matching without slotId, 409 conflict, 503, timeout/malformed/unexpected post-dispatch unknown and zero automatic POST retries.
- [x] T006 [P] Write failing extraction/rehearsal tests in `tests/test_interpretation.py` and `tests/test_openai_interpreter.py` for strict schema, nullable patches, missing/extra keys, bool/out-of-range ordinal, invalid dates/enums, refusal/incomplete/missing/duplicate output, bounded multi-turn input, `store:false`, model configurability, missing runtime key and safe live errors without fallback/effects; never put a real key in fixtures.
- [x] T007 [P] Write failing whitelist/emitter tests in `tests/test_events.py` for every allowed category/field, forbidden keys, bounded buffers/values, injected clock, immutable projections and sink copies; inject canary identities/secrets into query/body/prompt/errors and require zero leakage or raw exception text.
- [x] T008 [P] Write failing submission tests in `tests/test_submission.py` for serialized reserve-before-interpretation/effects, same-generation reentry, exceptions/in-flight/completed/failed/unknown receipts, distinct generations for repeated text, and no execution from edits/render/evidence inspection; assert effect call counts and no reopening after dispatch.
- [x] T009 Create isolated synthetic doubles/mock-process lifecycle helpers in `tests/helpers.py` and package markers `src/appointment_assistant/__init__.py` and `tests/__init__.py`; integrate failing foundation tests before implementation, keeping fixtures/date expectations derived from returned service data.
- [x] T010 Implement shared records/validation in `src/appointment_assistant/models.py` after T004/T009; preserve verbatim data-model constraints: Interpretation "no authority fields; null means no update"; preferences "Supported enums; valid calendar dates; start <= end; changes invalidate options/proposal/consent"; identity "Bounded private session values; valid date/ZIP; do not emit in evidence/logs"; candidates "Valid returned records; exactly one matching phone/DOB and, when ambiguous, privately supplied ZIP; never reveal candidate lists"; verified patient "Only core establishes this reference; identity-input changes clear verification and all dependent state; establishedPatient is a fact, not an invented restriction"; provider "Returned nonempty IDs/names, valid arrays/enums; public; keyed join for slot display"; slot "Returned available=true, aware timestamp, requested filters, known returned provider; ordered displayed options map ordinal to slot"; proposal "Private references; context-bound; summary must precede consent; choice alone never confirms"; appointment "201 plus matching patient/slot attributes and scheduled status; appointment has no slotId; private verified-patient disclosure only"; handoff "201 queued means mock accepted only; 503 failed; timeout/invalid successful response unknown; never human delivery"; receipt "Unique per explicit submit, reserve before interpretation/effects; same generation returns cached receipt, even after exceptions"; evidence "no external identifiers or free-text payload". Resolve only unspecified internal bounds explicitly in code/tests, without inventing backend/clinical restrictions.
- [x] T011 [P] Implement validated `urllib` scheduling adapter in `src/appointment_assistant/scheduling.py` after T005/T009/T010, covering only GET providers/patient search/patient appointments/availability and POST appointments/handoffs; default loopback4013 and 15-second finite timeout, bounded I/O, route-template diagnostics, known versus unknown errors, exact 201 matching and no automatic effect retry; pass T005.
- [x] T012 [P] Implement schema interface/local validation and visibly labeled credential-free deterministic rehearsal in `src/appointment_assistant/interpretation.py`, and `urllib` Responses adapter in `src/appointment_assistant/openai_interpreter.py` after T006/T009/T010; use `contracts/interpretation.schema.json`, default configurable `gpt-5.4-mini`, environment-only `OPENAI_API_KEY`, strict `text.format`, `store:false`, bounded relevant context without candidate records/API bodies, finite timeout and safe closed failures; model proposes intent/patch/ordinal only; pass T006.
- [x] T013 [P] Adapt standalone sanitized emitter in `src/appointment_assistant/events.py` after T003/T007/T009/T010 using only the interaction-contract whitelist: correlation token, sequence/time, category, intent/state/action enums, guard code/pass, HTTP method/route template/status, closed outcome/error/reason, option count and elapsed milliseconds; fixed templates, sink copies and bounds, never raw payload redaction; pass T007.
- [x] T014 [P] Adapt standalone generation gate in `src/appointment_assistant/submission.py` after T003/T008/T009/T010; reserve under serialized session handling before interpretation or effects, cache all receipt states and preserve unknown after dispatch exceptions; session-only guarantees with no durable API idempotency claim; pass T008.
- [x] T015 [P] Write failing real ZEN proposed-action policy tests in tests/test_policy.py for FR-018: public lookup, verified patient reads, current-slot/current-consent booking, unknown-write block, malformed facts and engine failure; no identity inputs.
- [x] T016 [P] Implement fixed rules/safety.json and src/appointment_assistant/policy.py with zen-engine==2.1.2 after T015; fail closed and require conversation.py to consume verdict before API effects, retaining independent transaction checks.
- [x] T017 Integrate foundation boundaries and run foundation tests with the compatible interpreter in `tests/test_models.py`, `tests/test_scheduling.py`, `tests/test_interpretation.py`, `tests/test_openai_interpreter.py`, `tests/test_events.py`, `tests/test_submission.py` and `tests/test_policy.py`; check vendor byte equality via `vendor/reference-api/manifest.json` before story work; this integration also depends on T016.

**Checkpoint**: All foundation tests pass; tests-first boundary lanes integrated. No user outcome claimed yet.

## Phase 3: User Story 1 — Find providers through conversation (P1)

**Goal**: Ordinary multi-turn provider discovery without unnecessary patient identity (FR-001–002, SC-001).
**Independent test**: Ask for downtown primary care with and without missing filters; service-returned facts only, zero patient calls, focused follow-up and truthful empty result.

### Tests first

- [x] T018 [US1] Write and run failing provider conversation tests in `tests/test_conversation.py` for FR-018 policy denial/engine-unavailable zero-API-effect assertions in `tests/test_conversation.py` (including `test_policy_denial_prevents_any_scheduling_effect`), AI/mode disclosure, retained multi-turn filters, unclear text, missing filters, only API-returned providers, empty/malformed responses and no identity collection/calls.
- [x] T019 [P] [US1] Write and run failing reusable-core/CLI submission tests in `tests/test_cli.py` for mode/API/model configuration, no key argument, no silent rehearsal, generation routing, deterministic `provider_lookup` demo and startup/reset disclosures.

### Implementation

- [x] T020 [US1] Implement deterministic public provider flow and bounded conversation context in `src/appointment_assistant/conversation.py` after T018; consume validated intent/patches, ask focused questions, display service facts only and keep patient verification out of public lookup.
- [x] T021 [US1] Implement thin conversational CLI and `provider_lookup` rehearsal demo in `src/appointment_assistant/__main__.py` after T019/T020; route explicit submissions through the gate, disclose AI/live versus rehearsal, configurable model/API and reset limitations, and verify T018/T019.
- [x] T022 [US1] Run an actual unchanged mock provider integration in `tests/test_acceptance.py` and the CLI provider demo; compare records privately and capture sanitized outcome/timing evidence in `docs/internal/demo.md` without treating rehearsal as live-model proof.

## Phase 4: User Story 2 — Identify a patient and confirm one booking (P1)

**Goal**: Unique verified identity, factual slots and one exact confirmed booking (FR-003–006, FR-010, SC-002–003).
**Independent test**: Synthetic happy path gets service slots, chooses then separately confirms an unchanged summary, produces exactly one validated scheduled appointment; negative consent cases produce zero POSTs.

### Tests first

- [x] T023 [US2] Write and run failing identity/availability/booking flow tests in `tests/test_conversation.py`: exact unique phone/DOB verification before availability, returned available slots/provider join/filter/timezone validation, invalid ordinal and no invented facts; reserve proposal attempt before POST and verify exact returned appointment attributes.
- [x] T024 [US2] Write and run failing consent tests in `tests/test_conversation.py`: only entire trimmed/casefolded current `yes` or `confirm` after prior-turn summary; selection alone, mixed/quoted/injected/old/model-generated affirmation, decline/abandonment, identity/search/intent/slot changes, reset, repeat confirmation and repeated generation never authorize an extra POST.

### Implementation

- [x] T025 [US2] Implement unique patient verification, preference gathering and returned-slot/provider joins in `src/appointment_assistant/conversation.py` after T023; quote-preserving T010 constraints apply, and zero/multiple matches stop patient-specific effects until US3 recovery exists.
- [x] T026 [US2] Implement exact context-bound proposal/summary, literal current consent, invalidation, reserve-before-POST and completed-result reuse in `src/appointment_assistant/conversation.py` after T024/T025; retain attempted/completed/rejected/unknown states and prohibit unknown replay, passing T023/T024.
- [x] T027 [US2] Add `happy_path_booking` CLI rehearsal sequence in `src/appointment_assistant/__main__.py` and actual mock acceptance cases in `tests/test_acceptance.py` after T026; run happy path and consent negatives, privately assert one matching appointment and zero unauthorized duplicates, and record sanitized results in `docs/internal/demo.md`.

## Phase 5: User Story 3 — Recover from unresolved identity (P1)

**Goal**: Private correction/ZIP recovery and selected verified appointment lookup (FR-003, FR-007–008, SC-004).
**Independent test**: No-match and duplicate fixtures expose no candidates; caller ZIP alone resolves a unique record or one correction ends with finite help. Appointment GET happens only after uniqueness and displays only that patient's returned records.

### Tests first

- [x] T028 [US3] Write and run failing identity recovery tests in `tests/test_conversation.py`: no-match, one unsuccessful correction then stop, duplicate-match private ZIP prompt without candidate facts, unique/missing/still-ambiguous ZIP, changed identity clearing state and no unverified availability/booking/disclosure.
- [x] T029 [US3] Write and run failing selected appointment lookup tests in `tests/test_conversation.py`: verify before supported GET, matched-patient validation, empty list versus malformed/missing array, 404/outage and no candidate/other-patient disclosure.

### Implementation

- [x] T030 [US3] Implement bounded no-match/ambiguity correction and private local ZIP comparison in `src/appointment_assistant/conversation.py` after T028; no ZIP query parameter, no candidate details, stop after unsuccessful correction with truthful human next step.
- [x] T031 [US3] Implement selected verified appointment lookup in `src/appointment_assistant/conversation.py` after T029/T030 and pass recovery/lookup tests; allow no patient-specific action under unresolved identity.
- [x] T032 [US3] Add `no_patient_match`, `multiple_patient_matches` and `appointment_lookup` demos in `src/appointment_assistant/__main__.py` and unchanged mock acceptance cases in `tests/test_acceptance.py`; run required no-match failure and selected recovery/lookup flows and record redacted results in `docs/internal/demo.md`.

## Phase 6: User Story 4 — Receive truthful help at scheduling boundaries (P1)

**Goal**: Finite safe recovery and selected real local handoff effects, without false outcomes/advice (FR-008–010, FR-012, SC-005).
**Independent test**: Permanent conflict, empty lakeside dermatology, outage, unsupported/medical/human requests, timeout and invalid POST success give distinct truthful next steps. Only validated handoff201 means queued; global503 means not queued; unknown effects never replay.

### Tests first

- [x] T033 [US4] Write and run failing boundary tests in `tests/test_conversation.py` for 409 clearing proposal/options and fresh service choice/consent, no availability, 503, medical/unsupported/human intent, invalid201/timeout/exception after dispatch as unknown, no clinical advice/invented contact details and reset/restart reconciliation warnings.
- [x] T034 [US4] Write and run failing handoff tests in `tests/test_conversation.py` for supported reason enums/fixed sanitized summaries, optional verified identity only, no automatic retries, offered/attempted/queued/failed/unknown distinctions, complete201 versus global503 or malformed success and no claimed human contact.

### Implementation

- [x] T035 [US4] Implement finite boundary responses/conflict fresh search and unknown-effect blocking in `src/appointment_assistant/conversation.py` after T033; stop unsupported/medical flows, require new selection/consent after conflict, and preserve unknown reconciliation across reset warnings without claiming durable state.
- [x] T036 [US4] Implement supported synthetic POST handoffs/reason templates in `src/appointment_assistant/conversation.py` after T034/T035; validated201 says queued only, 503 failed, timeout/invalid success unknown; no private transcript/identifiers in summary or invented delivery channel; pass T033/T034.
- [x] T037 [US4] Add `slot_conflict`, `handoff` and `api_failure --mock-scenario api_failure` demos in `src/appointment_assistant/__main__.py` and real-mock failure tests in `tests/test_acceptance.py`; use labeled `X-Mock-Scenario` only for fault injection, verify actual effect counts and record redacted success/failure/unknown outcomes in `docs/internal/demo.md`.

## Phase 7: User Story 5 — Understand outcomes and recovery as Support/Admin (P2)

**Goal**: Privacy-conscious diagnostics, redacted Lab evidence inspection and useful recovery guidance (FR-011–012, FR-015, SC-007). No admin console/authentication or role permissions implied.
**Independent test**: Review successful/failed/unknown synthetic flows; required event categories and timing present, canary private values absent, proposed action/guard/API evidence distinct, queued never means a human received it.

### Tests first

- [x] T038 [US5] Write and run failing integrated evidence tests in `tests/test_conversation.py` for intent/state, proposed action, guard result, API route-template/method/outcome, escalation reason and latency; inject private canaries in all adapter/core failure inputs and prove sinks/UI exports omit raw identifiers, messages, bodies, prompts, URLs and exception text.
- [x] T039 [P] [US5] Write and run failing thin Lab UI tests in `tests/test_lab_ui.py` for explicit form Send submission/new generation, unchanged generation reactive reentry and exceptions, repeated text as distinct submissions, edit/selection/theme/evidence rerenders with zero effects, AI/mode disclosure, separate literal confirmation, useful pending feedback and redacted projection.

### Implementation

- [x] T040 [US5] Wire fixed-template workflow/guard/interpretation/API/handoff/latency events into `src/appointment_assistant/conversation.py`, `src/appointment_assistant/scheduling.py` and `src/appointment_assistant/openai_interpreter.py` after T038; use only `events.py` projections, no raw upstream server audit import; pass T038 with private effect-count assertions.
- [ ] T041 [US5] Implement thin Marimo0.25.1 `apps/lab.py` after T039/T040/T014 using explicit form Send submissions through the session gate, default loopback28183/mock4013, all implemented flows, AI/mode disclosure, service-derived facts, exact summary/separate confirmation and proposed-action/guard/API evidence views; apply existing approved `assets/ui/ochsner-health-observed.svg` and `assets/ui/ochsner-observed-theme.css` without altering managed assets or adding nxusKit; pass T039.
- [ ] T042 [US5] Populate complementary recovery/diagnostic guidance in `docs/user/recovery.md` and `docs/internal/operations.md` after T040/T041; document known/attempted/completed/unknown, identity/outage reconciliation, queued versus delivered, privacy-safe evidence and raw server audit exclusion; retain unresolved Support/Admin Persona next step.
- [ ] T043 [US5] Exercise integrated CLI/Lab evidence and submit/edit/re-render/exception behavior against actual mock after T041; record sanitized evidence, platform/version and separate feedback/completion measurements in `docs/internal/demo.md`, and verify T038/T039 and prior stories without sensitive exports.

## Phase 8: User Story 6 — Reproduce and review the demonstration (P2)

**Goal**: Clean setup, usable demonstrations and truthful maintainer/reviewer handoff (FR-013–017, SC-006, preparation for SC-008). Actual video recording/submission remains separately authorized delivery, not fulfilled by notes.
**Independent test**: From a clean clone or labeled clean-copy equivalent on Mac ARM and Linux, use only declared prerequisites/instructions to install, run CLI/Lab and mock, reproduce required success/failure/reset and distinguish live interpretation from rehearsal. Report missing platform/model evidence as pending.

### Tests first

- [x] T044 [P] [US6] Write and run failing demo/reset acceptance tests in `tests/test_demo_acceptance.py` for all eight quickstart demo names, no ignored-RFP runtime paths, mock restart/fresh session, unknown-effect reset warning, dynamic returned dates/fixed-offset disclosure and sanitized repeatable outputs.
- [x] T045 [P] [US6] Write and run failing integrated live-interpreter double tests in `tests/test_live_conversation.py` proving real Responses-shaped multi-turn extraction feeds deterministic decisions, invalid/refused extraction produces no effect, and provider/booking/no-match workflows do not silently use rehearsal; doubles are labeled and do not prove live access.

### Implementation and qualification

- [x] T046 [US6] Complete demo/reset orchestration in `src/appointment_assistant/__main__.py` and integrate live interpreter with core in `src/appointment_assistant/conversation.py` after T044/T045; pass both test files and all prior story tests without editing supplied server or widening authority.
- [x] T047 [US6] Write complete clean setup, explicit Python3.11+ verification, editable install/Marimo pin, mock4013/Lab28183, environment-only live key configuration, CLI/rehearsal commands, reset/tests/demos, assumptions/limitations and concise document index in `README.md` and qualify steps in `specs/001-appointment-assistant/quickstart.md` after T046; distinguish memory/idempotency limits and fixture authentication from production security.
- [ ] T048 [US6] Qualify genuine synthetic multi-turn OpenAI provider/booking/no-match flows via CLI and Lab under existing local-live approval only when Implement runtime permits, using `gpt-5.4-mini` and environment-only key; record scenario/environment/load, model, measured feedback/completion and safe outcomes in `docs/internal/live-qualification.md`, never credentials/raw transcripts; missing access remains explicit pending and cannot be replaced by doubles or the supplied1.25-second background measurement.
- [ ] T049 [P] [US6] Qualify Mac ARM fresh clone or explicitly labeled clean-copy after T047 with explicit compatible Python and Marimo versions, declared install, full suite/required demos, Lab explicit-submit/edit/re-render and reset checks; record reviewed revision/copy identity, timings and actual outcomes or unavailable checks in `docs/internal/qualification-mac-arm.md` without publication.
- [ ] T050 [P] [US6] Qualify Linux fresh clone or explicitly labeled clean-copy after T047 in isolated state/ports, repeating declared install, full suite/required demos, Lab submit/edit/re-render and reset; record interpreter/Marimo, reviewed revision/copy identity, timings and actual outcomes or unavailable checks in `docs/internal/qualification-linux.md`; one host cannot establish both platforms.
- [ ] T051 [US6] Prepare tested <=5-minute walkthrough sequence and update `docs/internal/video-notes.md` and `docs/internal/demo.md` after T046–T050 results are known; cover provider/confirmed booking/no-match or handoff, architecture/methods, branding/Persona gaps and tradeoffs; distinguish tested/planned/recorded, external three-hour plus thirty-minute deadlines and unknown receipt/window evidence; do not claim the assigned-window statement without evidence or mark actual recording/submission complete.
- [x] T052 [US6] Add a small team modification exercise with expected affected-behavior checks in `docs/internal/development.md` after integrated code is stable; link canonical spec/tasks/tests and record genuinely performed versus pending exercise outcomes, without inventing Persona validation.

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Integrate before as-built handoff, verify actual sources/navigation, report limitations and consider optional improvements without creating a gate.

- [ ] T053 Run `PYTHONPATH=src python3 -m unittest discover -s tests -v` with verified Python3.11+ (project venv on PATH), actual unchanged mock and provider/booking/no-match success/failure demos in both CLI and Lab after T046; run selected ZIP/lookup/conflict/handoff/outage checks too, reset between modifying demos, inspect private API state/counts and record failures/timing honestly in `docs/internal/demo.md` before final as-built claims.
- [ ] T054 [P] Populate actual-code component/effect/data-flow architecture and diagrams in `docs/internal/as-built/architecture.md` after T053, based on stable `src/appointment_assistant/`, `apps/lab.py`, vendor and tests; stamp update date and reviewed source revision plus uncommitted state, explain deterministic authority/privacy/session limits and use working canonical links.
- [ ] T055 [P] Populate actual file/symbol/test walkthrough in `docs/internal/as-built/code-walkthrough.md` after T053 using implemented sources/tests, navigable links and relevant diagrams; stamp date/reviewed source revision plus uncommitted state; planned design remains in `plan.md`, and stubs never block earlier implementation.
- [ ] T056 [P] Reconcile implemented assumptions/decisions and short linked future work in `docs/product/decisions.md`, `docs/product/next-steps.md`, `docs/product/user-stories.md`, `docs/product/backlog.md`, `docs/product/roadmap.md` and `docs/product/sprint-planning.md` after T053; populated or explicitly deferred priorities/increments, native spec story links and tasks progress only, unresolved primary/Support/Admin/reviewer Personas and unavailable qualifications/video delivery remain honest.
- [ ] T057 [P] Update concise approved-asset/provenance index in `docs/internal/ui-assets.md` and milestone guidance in `docs/internal/milestones.md` after T053; consider optional post-MVP UI refinement with pre/post immutable annotated checkpoint tags and affected-behavior verification only if selected; existing assets/bootstrap controls stay unchanged and unselected refinement is explicitly deferred.
- [ ] T058 Consider one optional independent adversarial review per `docs/internal/reviews/adversarial-review.md` after T053, reuse adequate existing review when available, sanitize any findings and record selected/deferred disposition there; meaningful fixes require failing regression tests first, and review adds no mandatory MVP gate/proof cycle.
- [ ] T059 Main integrates T054–T058 and verifies README/document links, as-built navigation/diagrams against actual code/tests, date/revision stamps and final demo/video claims in `README.md`, `docs/internal/as-built/architecture.md`, `docs/internal/as-built/code-walkthrough.md` and `docs/internal/video-notes.md`; rerun affected suite/demos if new code changes require it and keep platform/live/recording gaps visible.
- [ ] T060 Main records verified outcomes and remaining work in `specs/001-appointment-assistant/tasks.md` and short linked `docs/product/next-steps.md`; before any authorized local commit/tag apply staged credential guard from `docs/internal/security.md`, preserve hooks, report incomplete scans without echoing suspected values, and push only ordinary milestones/tags to the verified approved private origin; never publicize or submit externally; actual video, external delivery and unavailable qualifications remain pending rather than checked off.

## Dependencies & Execution Order

- Setup T001–T003 precedes foundation. T002/T003 have disjoint vendor/license owners and can run together; T001 owns packaging/development docs.
- Foundation tests T004–T008 may run together; main T009 integrates helpers (test writers use local doubles until available). T010 waits on T004/T009. Implementation lanes T011–T014 wait on their own failing tests, T009/T010, and T003 for adapted patterns. T017 combines all lanes before story implementation.
- Story completion graph: `Setup → Foundation → US1 → US2 → US3 → US4 → US5 → US6 → T053 → {T054,T055,T056,T057} → T059 → T060`. T058 is an optional review consideration after T053. US2 needs US1 conversation skeleton; US3 needs US2 verified state; US4 needs their effect state; US5 needs stable workflows; US6 qualifies the integrated UI/core. Shared conversation/CLI/acceptance files have one main writer and are deliberately sequential. Each story is independently testable at its checkpoint with injected dependencies, even where implementation builds on earlier stories.
- Story workflow tests are consolidated in `tests/test_conversation.py`, owned and written sequentially by main. T018/T019 and T038/T039 can run concurrently only with distinct workflow-test versus CLI/UI owners; T023/T024, T028/T029 and T033/T034 share the consolidated file and must run sequentially. T044/T045 retain disjoint pending test files. Implementers wait for the relevant failing tests. No `[P]` implementation may overtake its tests. Contract/model constraints are fixed inputs, not a reason to skip red/green verification.
- T049/T050 depend on T047 and isolated platform/clone state; no shared ports, working tree writes or evidence files. T051 uses qualification results including explicit pending gaps. T053 waits on implemented components, not as-built stubs or video recording; final T059/T060 consumes all available qualification outcomes honestly.
- Main owns native files, shared core integrations and task status. Parallel workers receive exclusive listed files; no second writer to `conversation.py`, `__main__.py`, `test_conversation.py`, `test_acceptance.py` or native state. When platform/concurrency resources are unavailable or unsafe, run sequentially and state the constraint; no new orchestration service or scope reduction.

## Parallel execution examples per story

| Story | Eligible work after prerequisites | Owners / integration |
| --- | --- | --- |
| US1 | T018 provider tests + T019 CLI tests | A `test_conversation.py`, B `test_cli.py`; main implements T020/T021 after failures |
| US2 | T023 then T024 in the consolidated workflow suite | Main owns `test_conversation.py` and T025/T026; sequential shared-file work |
| US3 | T028 then T029 in the consolidated workflow suite | Main owns `test_conversation.py` and T030/T031; sequential shared-file work |
| US4 | T033 then T034 in the consolidated workflow suite | Main owns `test_conversation.py` and T035/T036; sequential shared-file work |
| US5 | T038 evidence tests + T039 UI tests | A `test_conversation.py`, B `test_lab_ui.py`; main wires adapters then UI |
| US6 | T044 demo tests + T045 live-double tests; later T049 Mac + T050 Linux | A/B disjoint test files, then isolated platform owners; main consumes results |

Foundation can use adapter owner A (T005/T011), interpreter owner B (T006/T012), event/gate owner C (T007/T008 then T013/T014), with main model/helper integration. Near completion, architecture owner A (T054), walkthrough owner B (T055) and product-doc owner C (T056) can draft concurrently after actual code stabilizes; main merges/validates T059. `[P]` is eligibility at its dependency checkpoint, not permission to race incomplete prerequisites.

## Implementation strategy

1. Build and verify Setup/Foundation, then US1 as the first independently useful provider-discovery increment. This is the suggested first MVP checkpoint, not the full accepted delivery scope.
2. Add US2 confirmed booking and US3 required no-match/privacy recovery; these plus US4 safety boundaries form the minimum end-to-end scheduling demonstration. Required diagnostics cannot be postponed merely because US5 is P2.
3. Complete all selected scope: verified appointment lookup, actual synthetic handoffs, safe conflicts/unknown effects, redacted Lab UI and CLI, reviewer reproduction and genuine multi-turn interpretation qualification. Model chooses no effects; same deterministic protections apply to both interfaces.
4. Integrate and test actual success/failure flows before as-built docs. Measure feedback separately from completion; developer/operator owns external time compliance. Final qualification reports unavailable platforms/access honestly without substituting simulation.
5. Finalize near-final architecture/walkthrough, clean README/index, team exercise and video notes; leave actual recording/external submission pending under their own authorization. Analyze remains a separate read-only stage and Converge a separately selected operation.

## Generation validation summary

60 tasks: Setup 3, Foundation 14, US1 5, US2 5, US3 5, US4 5, US5 6, US6 9, final cross-cutting 8. 23 `[P]` tasks are eligible only with satisfied prerequisites and exclusive files. All task IDs are sequential; native story phases retain `[USn]` labels. Workflow test tasks share `tests/test_conversation.py` and are sequential under one main owner. Pending dedicated acceptance/live/demo test tasks are still requirements, not claims that those files exist or are complete. Six independent story criteria remain defined above. This summary describes the plan, not implementation verification.

## Refinement analysis — 2026-10-08

Historical initial Analyze identified FR-018 engine coverage and corrected the final delivery restriction and starter decisions; that initial pass was not a claim that every severity was resolved. The subsequent all-severity artifact correction reconciled current versus historical stage wording, approved selected scope, the explicit ZEN constraint/checklist, dependency/setup pins, policy test inclusion and integration no-effect acceptance, consolidated workflow-test ownership, explicit form submission, minimal model context, task counts and success-status wording. Current scope is FR-001–018 / 60 tasks. These are artifact corrections only: Implement remains in progress, unchecked work and unqualified platforms/live flows/video remain pending, and no test/qualification completion is inferred from this analysis. Main owns task-status reconciliation and native files; independent owners do not commit or edit shared specs outside assigned ownership.

## Implementation evidence — 2026-10-09

Tests-first owned foundation/core lanes integrated.89 tests passed in26.118s using project Python3.11.13;8vendor hashes match. All8 rehearsal demos pass acceptance; required success/failure rerun. Genuine CLI OpenAI provider/book/no-match passed (live-qualification.md). Independent review3findings fixed with regressions; delta-only review11tests passed/no unresolved findings. Marimo form implementation exists but real repeated-submit qualification remains in progress after upstream chat metadata and input lifecycle findings; T041/T043 and dependent browser/platform handoff tasks stay unchecked. No video recording/public submission claimed.
