# Using Scheduling Lab

Updated2026-10-20. Follow the [README setup](../../README.md#setup). The banner identifies live OpenAI interpretation or deterministic rehearsal. Use synthetic data only.

Find primary care providers downtown without patient identity. For booking, provide phone and date of birth when asked; duplicate matches request ZIP privately and never list candidate patients. Select one returned option, review its summary, then send exactly yes or confirm in a separate message. Corrections invalidate prior consent. Ask to look up your appointments after identity verification or request a human.

This assistant cannot provide medical advice. A queued handoff is recorded only in the mock; no human contact is confirmed. [Recovery](recovery.md) explains failures, reset and unknown effects. All eight repeatable scenarios are in the [demo runbook](../internal/demo.md).

The [normal launcher](../../README.md#run) starts the synthetic API and browser in real model mode, using only the explicitly selected own-key Secure Note `[Env] OPENAI_API_KEY` notes field through your trusted helper. It makes no startup model request. `--interface cli` selects the same core; `--offline` explicitly selects rehearsal. Help/doctor are no-call; setup errors fail without fallback. The launcher browser uses port28454, and free alternate ports are supported without stopping other services. Ctrl-C cleans only children owned by that launch. Direct application commands remain an explicit environment-key alternative. Never enter a key into chat or browser controls.

Ochsner-supplied-key use is paused until further notice. Historical live evidence keeps its original account/source/date binding and is not own-key qualification. This policy update does not authorize new paid calls or relaunches.
