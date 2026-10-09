# Genuine live interpretation qualification

Updated2026-10-09. Mac ARM, explicit project Python3.11.13, one sequential synthetic session per scenario, no concurrent load; gpt-5.4-mini Responses structured extraction, store:false. Credential retrieved under explicit bounded user approval into process memory only; no credential/prompt/transcript saved. Unchanged supplied local mock; actual clinical backend not used.

CLI live runs at2026-10-09 05:00–05:01UTC:

| Scenario | Observed states | Total completion |
|---|---|---|
| provider_lookup | providers, validated GET200 |1029.7ms |
| happy_path_booking | identity→identity→slots→proposal→booked, matching POST201 |4615.9ms across5turns |
| no_patient_match | identity→identity→identity→handoff, no booking, mock queued201 |5170.7ms across4turns |

Interpretation calls ranged713.7–2001.8ms in this run. These are completion durations, not400ms feedback compliance. Browser feedback is separately checked; no SLA is asserted. Live browser qualification is in progress; [demo](demo.md) will record observed outcomes. Doubles in tests/test_live_conversation.py qualify deterministic boundaries only and are not this live proof. Missing/invalid model outputs never silently fall back to rehearsal.

## Controlled IAB live flow — 2026-10-09 00:27–00:34CDT

Revision7e9f930, MacARM main Lab28183/API4013. Genuine5turnbooking asked phone thenDOB, displayed actual3options, selection showed exactsummary withoutwrite; current separateyes produced matching201scheduledappointment. PrivateAPIcount was1beforeconfirmation,2after. Reset/no-match returned no candidates, human request actuallyqueued201 with nohumancontact claim. Genuine2turnprovider flow asked missinglocation then displayedAPIproviders foruptown. Form edits and evidence inspection didnotdispatch; successive sends worked after explicit debounce=False andstableformcell. UIfeedback: draftcleared by next toolAXcapture (~1–2s toolroundtrip); no400msclaim or browser-paint SLA. Completion timing is instrumented whitelistlatency, separately from UIfeedback. LinuxUI qualifiedseparately inrehearsal only.

Additional genuine CLI two-turn provider clarification passed: missing location prompted a focused question, then downtown returned API providers; 2516.5ms total process completion, no identity data or raw transcript exported.
