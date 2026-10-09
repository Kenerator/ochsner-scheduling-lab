# Recovery

Updated2026-10-09.

- No patient match: correct phone/DOB once or ask for a human; no candidate details are disclosed. Duplicate matches require your privately supplied ZIP.
- Conflict409: old choices and consent are cleared. Search again, select a fresh API option and separately confirm.
- Outage503: the global fault also blocks handoffs. Contact scheduling staff directly; the assistant cannot claim a queued request.
- Unknown booking or handoff: transport loss or malformed success cannot establish failure. Do not repeat the write. Contact staff to reconcile; no automatic retry occurs.
- Reset: send reset to clear conversation, or open a fresh session. Existing mock bookings remain. Restart only your own API process for fresh fixtures. Unknown effects block reset as a reconciliation boundary; restarting memory does not resolve them.

A valid201 booking is confirmed by matching returned patient and slot attributes. A valid201 handoff is **queued in the synthetic mock**, not delivered to a human. Evidence is nonidentity metadata; do not export raw API audit, prompts, transcripts or real identity data. [Runbook](../internal/demo.md).
