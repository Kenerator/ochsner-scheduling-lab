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

## Persona follow-on — 2026-10-09

Isolated genuine OpenAI IAB flow on mock4017/UI28187 (gpt-5.4-mini, synthetic fixtures, bounded environment-only credentials) verified current slots → invalid numbered choice9 → numbered options retained → choice1 → current summary with no repeated identity → Tab focuses Send → Enter submits separate yes → matching successful booking. Human request then displayed categorical known facts, Missing:none and Booking:completed, with queued mock/no-human-contact disclosure. After reset, partial primary-care request followed by human request showed missing phone/date-of-birth/location and Booking:not attempted. No raw transcript or identity values are saved in this report. The existing main mock/UI was untouched. Combined local suite:95 tests,28.280 seconds; eight rehearsal demos plus aliases and Marimo check passed. Source candidate is the subsequent persona-impact commit; prior platform reports remain revision-specific.

Delta review regression and genuine live IAB recheck also distinguish an earlier completed attempt from a corrected current identity/request: current booking not attempted; earlier attempt completed. Attempt revision binding prevents false current completion.

Exact committed candidate `66adbf54eb22020eb505f611f9545451b9888dfa` passed Mac ARM95 tests in28.289 seconds and Linux95 tests in30.829 seconds. Immutable RC-2 captured2026-10-09T01:37:03-05:00; private remote main and peeled tag matched and tree was clean. UI screenshot `/private/tmp/ochsner-persona-impact-66adbf5.png` is local proof, not footage.
