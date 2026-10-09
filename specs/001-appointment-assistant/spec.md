# Feature Specification: AI Appointment Scheduling Assistant

**Feature Branch**: No branch created; Git extension not configured.

**Created**: 2026-10-08

**Status**: Product implementation and synthetic qualification complete. Historical stage records remain below; [tasks and verification evidence](tasks.md) describe current outcomes. Actual video capture, named Persona validation and external delivery remain pending.

**Input**: Include client requirements indexed by `docs/product/RFP/README.md`; reconcile supplied intake with `docs/product/user-stories.md` and Persona mappings.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find providers through conversation (Priority: P1)

As a person seeking care, I want to ask in ordinary text which providers serve my requested specialty and location, clarify missing information over multiple turns, and see factual choices before deciding whether to book.

**Persona**: Jules and Ellie-Rae, exact hypothesis pins in [Personas](../../docs/product/personas.md). Fixture patients remain synthetic records, not Personas.

**Origin / scope**: SPECIFIED journey, reconciled from assignment Required 1–3 and supplied `provider_lookup`; accepted required scope. Narrative wording is normalized from those sources.

**Why this priority**: Provider discovery is independently useful and explicitly required, without collecting unnecessary patient identifiers.

**Independent Test**: In a fresh conversation ask for downtown primary care providers, including a version with missing specialty/location. Compare displayed providers with the scheduling service response; no patient identification is required.

**Acceptance Scenarios**:

1. **Given** a provider lookup request with specialty and location, **When** the assistant searches, **Then** it obtains matching providers from the supplied scheduling service and displays only returned names, specialties and locations.
2. **Given** a request missing information needed to narrow the user's search, **When** the assistant responds, **Then** it asks a focused follow-up and uses the answer in the same conversation without requesting phone or date of birth for public provider discovery.
3. **Given** an empty provider response, **When** results are explained, **Then** no provider is invented and the user receives a specific explanation and a supported next step.

### User Story 2 - Identify a patient and confirm one booking (Priority: P1)

As a person booking care, I want the assistant to identify my synthetic patient record, show available appointments, and book my chosen appointment only after I explicitly confirm its details.

**Persona**: Jules and Ellie-Rae; Sam-Rae (AGENT QA) probes stale consent/replay. Exact hypothesis pins in [Personas](../../docs/product/personas.md).

**Origin / scope**: SPECIFIED journey, assignment Required 1 and 4, booking policies and `happy_path_booking`; accepted required scope.

**Why this priority**: This is the required end-to-end consequential workflow; identity, factual options and confirmation protect the user from incorrect bookings.

**Independent Test**: Use the supplied happy-path patient fixture and a non-conflict downtown primary care slot. Supply missing information across turns, choose a displayed slot, confirm, and compare the resulting appointment with the scheduling service record.

**Acceptance Scenarios**:

1. **Given** booking intent and missing phone/date of birth or search preferences, **When** the conversation proceeds, **Then** the assistant gathers the missing information, identifies exactly one patient through the scheduling service and obtains availability for that patient before offering a booking.
2. **Given** returned available slots, **When** the assistant shows options, **Then** every offered slot is returned by the service, marked available, and described with its provider, specialty, location and date/time with timezone context.
3. **Given** a chosen displayed slot, **When** the user has not yet explicitly confirmed the summarized booking, **Then** no booking occurs; selecting a slot alone is not confirmation.
4. **Given** a uniquely identified patient and an explicitly confirmed, unchanged booking summary, **When** the assistant books, **Then** it sends the selected patient and slot to the scheduling service with confirmation recorded and reports the appointment only after the service confirms success.
5. **Given** a pending proposal, **When** the user declines, changes patient/slot/search details or ends the flow, **Then** no old confirmation authorizes a changed booking; a changed proposal requires a new summary and confirmation.
6. **Given** an already completed booking in the same conversation, **When** the user repeats confirmation, **Then** the assistant repeats the known result without creating another appointment. Cross-process or concurrent duplicate protection is not claimed.

### User Story 3 - Recover from unresolved identity (Priority: P1)

As a person whose record cannot be uniquely identified, I want a clear explanation and safe clarification or human assistance instead of guessed identity or disclosure of someone else's appointments.

**Persona**: Ellie-Rae and Jules, including unresolved identity; exact hypothesis pins in [Personas](../../docs/product/personas.md). No demographic or diagnostic attributes inferred.

**Origin / scope**: SPECIFIED journeys from `no_patient_match`, `multiple_patient_matches`, identity policies and assignment failure table; accepted identity-safety scope. No-match is the required demonstrated failure. Multiple-match safeguards apply to booking even though existing-appointment lookup is optional.

**Why this priority**: Required failure handling and mandatory privacy rules apply before any patient-specific action.

**Independent Test**: Exercise the supplied no-match identifiers and the duplicate-match fixtures; inspect user-visible responses and recorded operations for data disclosure and forbidden bookings.

**Acceptance Scenarios**:

1. **Given** no patient match, **When** identification completes, **Then** the assistant exposes no patient or appointment data, asks for corrected/additional identifying information, and offers a human next step rather than guessing or booking. If the user cannot resolve the mismatch, the flow stops with that next step.
2. **Given** multiple matching patients, **When** identification completes, **Then** the assistant asks the user to supply a distinguishing ZIP code without displaying candidate identifiers or appointment details and proceeds only if exactly one returned record matches.
3. **Given** ambiguity that persists after clarification, **When** the assistant responds, **Then** it stops patient-specific actions, explains unresolved identity and provides a truthful human-assistance next step.
4. **Given** a request for existing appointments, **When** that optional capability is absent, **Then** it is treated as unsupported and directed to human assistance without revealing patient data. If implemented later, the same identity checks apply first.

### User Story 4 - Receive truthful help at scheduling boundaries (Priority: P1)

As a person encountering unavailable scheduling or an unsupported request, I want a specific explanation and a finite next step, with no fabricated outcome or medical advice.

**Persona**: Jules and Morgan-Rae (human support), with Sam-Rae (AGENT QA) safety probes. These hypothesis mappings grant no clinical authority.

**Origin / scope**: SPECIFIED policies, assignment safety description and supplied `slot_conflict`, `no_availability`, `api_failure`, `unsupported_request`; accepted baseline safe-stop behavior. Richer alternate-search recovery and recorded handoff delivery remain optional.

**Why this priority**: Policy boundaries are mandatory even though the assignment requires demonstration of only one failure case.

**Independent Test**: Exercise the permanent conflict slot, empty lakeside dermatology search, service outage, medical-advice request, unsupported specialty and explicit human request. Verify specific explanations and absence of invented records or advice.

**Acceptance Scenarios**:

1. **Given** an empty availability response, **When** results are explained, **Then** no slot is invented, the user is told nothing matching is available and receives a human next step; an alternate search may be offered only within supported scope.
2. **Given** the selected slot is rejected as taken, **When** booking fails, **Then** the assistant states that it was not booked and offers a human next step or newly obtained available options requiring a new confirmation.
3. **Given** scheduling service unavailability, **When** an operation fails, **Then** the assistant explains the outage, stops automatic attempts and provides a human-assistance next step without claiming a successful booking or delivered handoff.
4. **Given** a request for medical advice, a human, an unsupported specialty/location/appointment type or another unsupported action, **When** it is recognized, **Then** the assistant gives no medical advice or triage, stops the unsupported flow and explains the relevant human next step.
5. **Given** an interrupted booking whose effect is unknown, **When** responding or resuming, **Then** the assistant labels the outcome unknown, does not blindly repeat the booking, and directs reconciliation to human assistance.

### User Story 5 - Understand outcomes and recovery as Support/Admin (Priority: P2)

As the mapped support/admin teammate, I want accurate, privacy-conscious outcome and recovery context so I can help without making the user repeat work or taking unsafe action.

**Persona**: Morgan-Rae (human support hypothesis), exact pin in [Personas](../../docs/product/personas.md); mapping grants no console or access rights.

**Origin / scope**: INFERRED story wording migrated from the draft seed; basis is supplied observability/privacy policies plus Constitution support coverage. Required diagnostic information is accepted because policies explicitly require it; no admin console, authentication system or live support delivery is added.

**Why this priority**: Safe support requires distinguishing attempted, completed and unknown actions; this does not depend on a new support application.

**Independent Test**: Review sanitized diagnostic output and recovery documentation from successful and failed synthetic conversations without access to full patient identifiers or secrets.

**Acceptance Scenarios**:

1. **Given** a completed or failed conversation step, **When** permitted diagnostics are reviewed, **Then** intent/workflow state, scheduling calls, outcomes/errors, escalation reason where relevant and measured latency are distinguishable without plaintext full phone/date of birth, other sensitive identifiers or secrets.
2. **Given** unresolved identity, outage or uncertain booking effect, **When** recovery guidance is inspected, **Then** known facts, missing information, attempted/completed/unknown outcomes and the next safe step are distinct; it does not assert a human received a request without evidence.

### User Story 6 - Reproduce and review the demonstration (Priority: P2)

As a developer or reviewer, I want complete local setup and a concise walkthrough so I can reproduce the required flows and understand the assistant's limitations.

**Persona**: Sam-Rae (AGENT QA hypothesis) for reproducible checks; Morgan-Rae for human support inspectability. Persona/tool text grants no action authority.

**Origin / scope**: INFERRED narrative based on explicit assignment submission/definition-of-done requirements and Constitution demonstration/documentation requirements; those underlying requirements remain accepted. External submission is not authorized by this specification.

**Why this priority**: Reproducibility makes behavior and boundaries assessable rather than relying on claims.

**Independent Test**: Follow documented prerequisites and setup from a clean project copy, start the supplied mock service, run the assistant, and reproduce provider lookup, booking and no-match failure using synthetic data.

**Acceptance Scenarios**:

1. **Given** a clean project copy and declared prerequisites, **When** the README instructions are followed, **Then** the provided mock service and assistant run without undocumented setup, and reset restores the documented synthetic starting state.
2. **Given** the required flow demonstrations, **When** client delivery is prepared in an authorized later stage, **Then** an actual walkthrough video of at most five minutes covers provider lookup, confirmed booking, one failure/handoff, architecture, assumptions and tradeoffs; a script is not evidence of a recorded video and recording/submission remain pending during Specify.
3. **Given** a review of project documentation, **When** known limitations and next steps are inspected, **Then** optional/unbuilt capabilities, mock versus real behavior, Persona validation gaps, setup/test commands and timing evidence are stated honestly. A small team modification exercise and actual-code architecture/walkthrough are completed after integration, not assumed from stubs.

### Edge Cases

- Empty or unclear text: ask a focused follow-up; do not infer permission to book.
- Invalid phone/date format, unsupported filters or malformed scheduling response: explain the problem and allow correction where safe; do not invent service results.
- Several patient matches with the same name, phone and birth date: ZIP is the fixture discriminator; name alone does not resolve identity.
- A chosen slot outside the displayed options or no longer available: reject it or obtain new options; do not reuse old confirmation.
- An earlier affirmative utterance, a model-generated affirmative statement or changed request: none authorizes the current booking.
- Outage also affecting optional handoff recording: acknowledge that delivery failed or is unknown; a queued synthetic receipt does not mean human contact occurred.
- Fresh conversation or restarted service: no inherited identity or confirmation; reset behavior and in-memory limitations are disclosed. An unknown prior booking effect must not be treated as failed merely because state was reset.
- Returned date/time uses the supplied fixed timezone offset; do not imply daylight-saving correctness. Fixture-only date-generation/conflict fields cannot be used to bypass service behavior.
- Public provider lookup must not turn into unnecessary patient identification; patient-specific requests must never reuse an unverified identity.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The assistant MUST disclose that it is AI, accept ordinary text over multiple turns, distinguish provider lookup from booking, and ask focused questions for missing information while retaining relevant context within the conversation. Acceptance: Stories 1.1–2, 2.1; disclose AI at conversation entry.
- **FR-002**: Provider discovery MUST obtain matching providers from the supplied mock scheduling service and show only returned facts; public lookup MUST NOT require patient identification. Acceptance: Story 1.1–3.
- **FR-003**: Before availability requests for a patient, booking or any implemented patient-specific appointment disclosure, the assistant MUST identify exactly one patient through the scheduling service using the supplied phone/date-of-birth identification flow. It MUST request clarification for multiple matches and stop if identity remains unresolved. Acceptance: Stories 2.1, 3.1–4.
- **FR-004**: Booking options MUST be obtained from the supplied scheduling service for the identified patient and supported preferences; only returned available slots may be offered with understandable provider, specialty, location and date/time details. Acceptance: Story 2.2; edge case invalid selection.
- **FR-005**: The assistant MUST summarize the exact patient-bound booking proposal and obtain explicit user confirmation before booking. Slot selection, prior unrelated consent and model reasoning MUST NOT supply confirmation; changed details invalidate it. Acceptance: Story 2.3–5.
- **FR-006**: A confirmed booking MUST use the selected service-returned patient/slot and true confirmation, and MUST report success only from a successful scheduling response. Repeated confirmation of a completed proposal in the same conversation MUST NOT cause another booking. Acceptance: Story 2.4, 2.6.
- **FR-007**: No-match identification MUST expose no patient/appointment data, request clarification and provide a finite human next step when unresolved, without guessing a patient. Acceptance: Story 3.1, 3.3; required failure demonstration.
- **FR-008**: Medical-advice requests MUST receive no advice or triage; human requests, unsupported scheduling scope, unresolved identity and downstream unavailability MUST stop the affected flow with a specific explanation and human-assistance next step. Acceptance: Stories 3.3–4, 4.3–4.
- **FR-009**: Empty availability and rejected slots MUST receive truthful explanations and a supported next step without invented options or false bookings; any replacement booking requires fresh confirmation. Acceptance: Story 4.1–2.
- **FR-010**: Uncertain booking effects MUST be distinguished from known failures and completed bookings; automatic replay is prohibited until reconciliation. Declined or abandoned proposals MUST produce no booking. Acceptance: Stories 4.5, 2.5.
- **FR-011**: Diagnostics MUST record intent/workflow state, calls to the scheduling service, outcomes/errors, escalation reason and basic latency while excluding secrets, full phone/date of birth and other sensitive identifiers in plaintext. Acceptance: Story 5.1.
- **FR-012**: User messages and support documentation MUST distinguish offered human assistance from an attempted, accepted, failed or unknown handoff. No live human delivery may be asserted from a synthetic queued receipt. Acceptance: Stories 4.3, 5.2; handoff-outage edge case.
- **FR-013**: The README MUST provide complete setup/prerequisites, starting the supplied mock, running the assistant, reset, any test/evaluation commands, architecture, decisions, assumptions, tradeoffs, limitations and next steps, with a concise working document index. Acceptance: Stories 6.1, 6.3.
- **FR-014**: Client delivery MUST include an actual walkthrough video of at most five minutes covering provider lookup, one end-to-end confirmed booking and at least one failure/handoff, plus architecture/tradeoffs. Supporting demonstration material MUST distinguish planned material from actual tested or recorded behavior; a script alone does not fulfill the video requirement. Recording and submission are deferred to an authorized later delivery stage. Acceptance: Story 6.2.
- **FR-015**: The PoC MUST retain synthetic fixtures, expose no real patient data or committed secrets, and document that fixture identity checks and mock effects are not production authentication, clinical advice or compliance certification. Acceptance: inspect all required demo outputs, diagnostics and delivery documentation; Stories 3, 5 and 6.
- **FR-016**: Maintainer/support documentation MUST include a small team modification exercise and, after integration, actual-code architecture and code/test walkthrough with update date, reviewed revision, working navigation and diagrams. These are completion artifacts, not prerequisites to begin implementation. Acceptance: Story 6.3.
- **FR-017**: Delivery documentation MUST record the assignment's three-hour code/README window and video deadline thirty minutes later, distinguish measured timing from unknown timing, and only include the requested statement “I completed this within the assigned 3-hour window.” when supported by evidence. Repository sharing and video submission MUST remain subject to separate authorization. Acceptance: Story 6.3 and timing/documentation review.

### Key Entities *(include if feature involves data)*

- **Conversation**: User messages, interpreted intent, missing information, uniquely identified synthetic patient if any, current search preferences, proposed slot, confirmation status and known operation outcome. Identity and confirmation are conversation-scoped.
- **Patient match**: Scheduling-service record identifying a synthetic patient; phone/date of birth support search and ZIP supports duplicate-match clarification. This is not real-user authentication.
- **Provider**: Service-returned provider identity, name, specialty, supported locations and modalities. A provider listing does not by itself prove slot availability.
- **Available slot**: Service-returned slot identity, provider, specialty, location, date/time and availability; availability may change before booking.
- **Booking proposal / appointment**: Proposal binds an identified patient and displayed slot to explicit confirmation; appointment is the service-confirmed result and status, not a model prediction.
- **Outcome / handoff context**: Known facts, missing information, operation attempt/result, escalation reason and next safe step; optional recorded handoff has a service receipt and status, which does not prove human contact.
- **Diagnostic event**: Sanitized intent/state, scheduling operation, outcome/error, escalation reason and elapsed duration, without sensitive identifiers or secrets.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In all required provider-lookup acceptance cases, users see only service-returned matching providers and supply no patient identifiers; missing search information is resolved through at least one follow-up turn.
- **SC-002**: In the happy-path demonstration, a synthetic existing patient completes one downtown primary care booking over multiple turns; exactly one appointment is created after explicit confirmation and the displayed result matches the scheduling record.
- **SC-003**: In 100% of the non-confirmation, decline, changed-proposal, invalid-slot and repeat-confirmation cases, no unauthorized or duplicate appointment is created within the same conversation.
- **SC-004**: In all no-match and duplicate-match acceptance cases, zero unverified patient-specific appointments are disclosed or booked; unresolved cases end with a specific explanation and human next step.
- **SC-005**: In all tested outage, empty-availability, slot-conflict, unsupported-request and medical-advice cases, users receive a truthful reason and finite next step; there are zero invented scheduling results, clinical recommendations or false delivered-handoff claims.
- **SC-006**: A reviewer following only the documented instructions from a clean project copy reproduces all three required demonstrations without undocumented setup; documented reset restores their starting conditions. Timing and feedback/completion latency are reported for the measured scenarios without unmeasured capacity claims.
- **SC-007**: Support/reviewer inspection of required diagnostic events finds every required context category and zero plaintext secrets, full phone/date of birth or other sensitive identifiers; attempted, completed and unknown outcomes are correctly distinguishable in all recovery examples.
- **SC-008**: The required actual walkthrough video lasts no more than five minutes and shows all required demo flows with architecture/tradeoffs; known gaps and simulated effects are disclosed. Supporting documentation has working links to the canonical specification and, when implemented, actual-code/test documentation. This outcome remains pending until a recording exists; a script is preparation only.

## Assumptions

### Reconciled scope and source precedence

The original Specify-stage optional labels below describe intake scope at that time. Current accepted Lab scope additionally includes the selected Marimo UI, verified existing-appointment lookup, private ZIP disambiguation, recorded synthetic handoffs and supported fresh-search recovery described in [plan.md](plan.md). These selections do not authorize live human delivery, public publication or production effects.

- The [RFP index](../../docs/product/RFP/README.md) and [manifest](../../docs/product/RFP/manifest.json) identify the supplied assignment, policies, scheduling contract, mock-service documentation/reference code, suggested scenarios and fixtures. All eleven text entries were read, with assignment first and its policy/contract/mock references in the requested order. Reference code was inspected, not executed during Specify.
- The only indexed attachment is `.DS_Store`, identified as Apple Desktop Services Store metadata. It was not interpreted as a requirements document; no requirements-bearing document attachment is present in this manifest. Do not claim its contents were reviewed.
- Assignment Required 1–5 define the minimum flow. Policies impose safety and observability requirements across supported paths; their requirements are not downgraded by the optional enhancements list. `no_patient_match` is the highest-priority required failure demonstration. `multiple_patient_matches` is labeled required in supplied scenarios and is covered as an identity safeguard; its example uses optional existing-appointment lookup, which remains optional rather than silently expanding the minimum flow.
- The adopted [brief](../../docs/product/brief.md) now reflects this client's multi-turn, supplied-service requirement; the generic one-operation starter brief was superseded. The current [Lab decisions](../../docs/product/decisions.md) have replaced the historical starter execution decisions and align with the selected plan. The Constitution and bootstrap controls remain unchanged. The separate bootstrap synthetic text-normalization qualification example is infrastructure reference, not this client feature.
- No named Persona is pinned in supplied mappings. Explicit unresolved primary-user, Support/Admin and reviewer placeholders are retained; selecting and validating constraint-rich Personas is a next step, not invented research or a gate preventing the required flow. Draft Support/Admin narrative has been migrated here with inferred origin distinct from the explicit policy requirements it supports.

### Optional capabilities and boundaries

- Existing-appointment lookup, recorded synthetic handoffs, richer alternative-slot/search recovery, an additional graphical interface, a separate scenario evaluation harness, expanded per-step traces and production cost/rollout notes are supplied good-to-have candidates, not implied authorization or prerequisites to the minimum flow. Basic policy diagnostics and safe-stop behavior remain required.
- Reschedule and cancellation of existing appointments are outside required prototype scope; declining a proposed booking remains required. Strong real-user authentication, real clinical data, live scheduling, live human delivery, durable distributed replay protection and production deployment are outside this authorized local stage.
- Basic human assistance can be a truthful instruction to contact scheduling staff; no contact number, delivery channel or staffed service has been supplied, so none may be invented. The optional handoff-recording enhancement must use only supported reason categories and sanitized context if subsequently selected.
- The supplied scheduling mock is the source of provider, patient, slot and appointment facts. Its in-memory bookings reset on restart; dates are relative to the server's current day with a fixed offset and no daylight-saving handling. Tests must use returned dates rather than assume literal calendar dates, and must not depend on fixture-only conflict/date-generation fields as user-visible service data.
- Required AI conversation behavior is specified here; provider/model configuration and its deterministic decision boundaries belong in planning. Credential access, external model calls, publication and deployment are not granted by the intake or this stage. A local synthetic path must remain usable without credentials; simulation must be labeled and cannot be represented as proof of live model behavior.

### Effort, delivery and performance

- The supplied assignment requests three hours from package receipt for code/README, a video thirty minutes later, a repository link and a specific time-compliance statement. Actual receipt time, deadline and historical work-window evidence are not supplied. This stage establishes requirements, not a completion/time-compliance claim. The developer/operator owns external effort-budget compliance and tradeoffs; elapsed estimates cannot silently shrink mandatory scope. Sharing needs a separate destination/privacy grant.
- Useful feedback targets approximately 400 milliseconds where feasible, separately from longer operation completion; actual feedback/completion measurements must identify scenario, environment and load. No client concurrency, throughput or full-response deadline was supplied, so none is invented as a release gate.
- Historical Specify-stage record: that invocation selected Specify only and performed no implementation, plan/tasks generation, credential access, commit, push, recording or external submission. The current cumulative target is Implement; execution authority comes from the Operator's separate grants, not this specification.

### Supplied scenario traceability

| Supplied scenario | Native acceptance coverage | Scope reconciliation |
| --- | --- | --- |
| `provider_lookup` | Story 1; FR-001–002; SC-001 | Required provider discovery without patient identity collection |
| `happy_path_booking` | Story 2; FR-003–006; SC-002–003 | Required multi-turn confirmed booking |
| `no_patient_match` | Story 3.1, 3.3; FR-007; SC-004 | Selected required failure demonstration |
| `multiple_patient_matches` | Story 3.2–4; FR-003; SC-004 | Required identity safeguard; optional existing-appointment feature remains optional |
| `slot_conflict` | Story 4.2; FR-009; SC-005 | Required truthful boundary; richer replacement-slot recovery optional |
| `no_availability` | Story 4.1; FR-009; SC-005 | Required truthful boundary; alternate search optional |
| `api_failure` | Story 4.3; FR-008, FR-012; SC-005 | Required safe stop; recorded handoff optional and cannot be claimed if also unavailable |
| `unsupported_request` | Story 4.4; FR-008; SC-005 | Mandatory no-medical-advice boundary |

### Historical Specify-to-Plan handoff

Reconcile the starter brief/decisions, plan the required flows and synthetic service boundary, select/validate unresolved Personas, and schedule tests before behavior changes. Later Tasks must include near-final as-built documentation work based on stable implemented components and final combined verification. At that historical handoff no plan or tasks existed. They now exist in [plan.md](plan.md) and [tasks.md](tasks.md); specification validation remains distinct from implementation evidence.

## Approved Lab scope refinement — 2026-10-08

**FR-018**: The Lab MUST invoke ZEN 2.1.2 for a meaningful proposed-action safety decision before scheduling operations. Validated nonidentity facts describe operation, verified identity, current API slot, current explicit consent and unknown prior booking outcome. Denial or engine failure prevents the effect; deterministic code retains independent identity/consent/transaction guards. The developer inspector shows the fixed verdict/reason without raw inputs. This is an accepted Operator/Manager refinement, not an inferred clinical requirement. No Bayesian, solver or CLIPS behavior is selected because no supplied requirement needs it. Tests must prove real engine decisions and no-effect denial/failure.
