# Scheduling HTTP adapter contract

Updated: 2026-10-08. Implement only the supplied contract; base URL defaults to `http://127.0.0.1:4013`. The unchanged vendored OpenAPI will be `vendor/reference-api/openapi/scheduling-api.yaml`; planning source is `docs/product/RFP/source/openapi/scheduling-api.yaml`.

| Request | Parameters/body | Accepted success | Expected failure |
| --- | --- | --- | --- |
| GET /providers | optional specialty/location | 200 providers array | 400, 503 |
| GET /patients/search | required phone/dob | 200 matches array | 400, 503 |
| GET /patients/{patientId}/appointments | verified patientId in path | 200 appointments array for that patient | 404, 503 |
| GET /availability | verified patientId, specialty; optional location/startDate/endDate | 200 available slots array | 400, 503 |
| POST /appointments | patientId, slotId, confirmed=true from deterministic core | 201 validated appointment | 400, 409, 503 |
| POST /handoffs | reason, fixed sanitized summary; optional verified patientId | 201 nonempty handoffId and status=queued | 400, 503 |

Specialties: `primary_care`, `dermatology`. Locations: `downtown`, `uptown`, `lakeside`. Handoff reasons: `user_requested`, `identity_unclear`, `unsupported_request`, `medical_advice`, `api_failure`, `no_availability`, `other`.

## Boundary rules

Use urllib URL encoding and JSON bodies, bounded requests/responses and explicit finite timeout (planned default 15 seconds). Reject invalid inputs before I/O. Validate success envelope/list/entity types, nonempty IDs, booleans, enums and dates independently; Python bool is not an integer ordinal. Missing arrays are malformed, not empty results. Validate returned records against query/verified patient. Do not infer clinical or established-patient eligibility.

Public provider lookup requires no identity. Patient lookup is literal phone/DOB equality; ZIP is not a supported query parameter. Core compares caller ZIP privately against candidates. Patient-specific operations require one verified match. Slot names join returned providers; reject missing/mismatched provider facts rather than invent names. Do not ingest fixture-only date/conflict fields through application contracts.

A booking success is exactly HTTP 201 with complete validated appointmentId, matching patientId, providerId, specialty, location and startTime, and status `scheduled`. Response has no slotId; compare returned attributes to the selected slot. Other 2xx or malformed/mismatched 201 after POST is unknown. Timeout, lost connection or unreadable response after dispatch is unknown; no automatic POST retry. Validated 409 means conflict, not booking: clear proposal and obtain fresh returned options, selection and consent. Expected known errors have finite next steps; raw server error messages are not diagnostic payloads. Unexpected server/transport responses after an effect are conservatively unknown.

A handoff success is exactly validated 201 queued, meaning synthetic storage only. 503 means unable to queue; timeout/malformed success means unknown. Never blindly retry handoff effects or claim a person was contacted. Only verified identity may supply optional patientId, and summary excludes private identifiers/transcript/clinical detail.

The reference server supports `X-Mock-Scenario: api_failure` for deterministic 503 on every route, including handoffs. Use only as labeled fixture fault injection. Restart resets store; relative dates use fixed `-05:00`, without DST guarantees. No status-by-proposal, idempotency, reschedule, cancel or human-delivery endpoint exists.

## Diagnostics

Emit route templates, method, status, duration and closed error class, never raw URL/query/body or patient path. The unchanged upstream server's stdout audit can contain a patientId in the appointments path; it is not approved redacted application evidence. Keep raw upstream logs out of exported evidence and shared artifacts.
