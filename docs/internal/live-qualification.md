# Genuine live interpretation qualification

Updated2026-10-09. Mac ARM, explicit project Python3.11.13, one sequential synthetic session per scenario, no concurrent load; gpt-5.4-mini Responses structured extraction, store:false. Credential retrieved under explicit bounded user approval into process memory only; no credential/prompt/transcript saved. Unchanged supplied local mock; actual clinical backend not used.

CLI live runs at2026-10-09 05:00–05:01UTC:

| Scenario | Observed states | Total completion |
|---|---|---|
| provider_lookup | providers, validated GET200 |1029.7ms |
| happy_path_booking | identity→identity→slots→proposal→booked, matching POST201 |4615.9ms across5turns |
| no_patient_match | identity→identity→identity→handoff, no booking, mock queued201 |5170.7ms across4turns |

Interpretation calls ranged713.7–2001.8ms in this run. These are completion durations, not400ms feedback compliance. Browser feedback is separately checked; no SLA is asserted. Live browser qualification is in progress; [demo](demo.md) will record observed outcomes. Doubles in tests/test_live_conversation.py qualify deterministic boundaries only and are not this live proof. Missing/invalid model outputs never silently fall back to rehearsal.
