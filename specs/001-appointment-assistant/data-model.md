# Data model

Updated: 2026-10-08. Planned application records; external field names remain the supplied API's camelCase. No persistence or production identity guarantee.

| Entity | Fields / relationships | Validation and visibility |
| --- | --- | --- |
| Interpretation | intent, fixed nullable field patches, option ordinal | [Closed schema](contracts/interpretation.schema.json); no authority fields; null means no update |
| Search preferences | specialty, location, start/end date | Supported enums; valid calendar dates; start <= end; changes invalidate options/proposal/consent |
| Identity input | phone, DOB, optional ZIP | Bounded private session values; valid date/ZIP; do not emit in evidence/logs |
| Patient candidates | API patientId, names, DOB, phone, ZIP, establishedPatient | Valid returned records; exactly one matching phone/DOB and, when ambiguous, privately supplied ZIP; never reveal candidate lists |
| Verified patient | Unique candidate for current identity context | Only core establishes this reference; identity-input changes clear verification and all dependent state; establishedPatient is a fact, not an invented restriction |
| Provider | API providerId, name, specialty, locations, modalities | Returned nonempty IDs/names, valid arrays/enums; public; keyed join for slot display |
| Slot | API slotId, providerId, specialty, location, startTime, available | Returned available=true, aware timestamp, requested filters, known returned provider; ordered displayed options map ordinal to slot |
| Proposal | local proposal generation, context revision, verified patient ref, selected returned slot, exact displayed summary, state | Private references; context-bound; summary must precede consent; choice alone never confirms |
| Appointment | API appointmentId, patientId, providerId, specialty, location, startTime, status | 201 plus matching patient/slot attributes and scheduled status; appointment has no slotId; private verified-patient disclosure only |
| Handoff | reason enum, fixed sanitized summary, optional verified patient ref, attempt state, validated receipt | 201 queued means mock accepted only; 503 failed; timeout/invalid successful response unknown; never human delivery |
| Submission receipt | session generation, reserved state, result/error classification | Unique per explicit submit, reserve before interpretation/effects; same generation returns cached receipt, even after exceptions |
| Evidence event | sequence, relative correlation token, timestamp, category/status, intent/state, route template, outcome/error class, reason, duration | Fixed whitelist in [interaction contract](contracts/interaction.md); no external identifiers or free-text payload |

## Conversation state

Private session holds current intent/preferences, bounded interpretation context, identity inputs/candidates/verified record, displayed options, current proposal, last outcome, handoff receipt, submission receipts and redacted event buffer. Keep model context minimal; do not send returned patient candidate records, full API bodies, credentials or sensitive evidence. Synthetic identity values needed for field extraction are runtime input, never logs. Deterministic summaries render user-visible service facts; model text is not displayed as scheduling truth or clinical advice.

### Workflow transitions

1. Entry discloses AI and live versus deterministic rehearsal mode. Public provider request gathers supported filters then calls providers without identity.
2. Booking/appointment lookup gathers identity; zero matches asks for correction and, after one unsuccessful correction, ends with human assistance. Multiple matches requests caller ZIP privately; if still not unique after one correction, stops. No availability or appointment calls before uniqueness.
3. Booking gathers preferences, calls availability and providers, validates and displays joined options. An ordinal selects only from these options; invalid choice leaves no authorized proposal.
4. Selection creates a new context-bound proposal and renders exact summary. A separate current whole-message `yes` or `confirm` authorizes it. Context changes, decline, abandonment or reset invalidate pending proposal/consent; mixed messages do not confirm.
5. Reserve submission generation before any model/API effects; reserve proposal attempt before POST. Attempt transitions to completed on validated 201, rejected on known 400/409/503, unknown on timeout or invalid successful response. Unexpected post-dispatch errors cannot reopen the proposal for retry.
6. `409` clears stale proposal/options and offers fresh search/choice/consent or handoff; do not invent an alternate slot. Repeat completed confirmation returns prior outcome without POST. Unknown remains blocked pending human reconciliation, including reset warning; reset is not evidence of failure.
7. Handoff stops the affected flow, sends only supported reason/template summary and optionally verified patientId. Keep offered, attempted, queued, failed and unknown separate. Global outage can also reject handoff.

UI editing, rendering or evidence inspection never advances state or effects; only a new submitted generation enters the core. Session restart loses receipts; no distributed or durable guarantee is claimed.
