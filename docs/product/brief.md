# Product brief

Updated: 2026-10-09.

Build a synthetic Ochsner appointment assistant that helps users find providers, verify a mock patient, inspect appointments and available slots, and book only after a separate explicit confirmation of the current summary. A truthful queued mock handoff supports no-match, unsupported and medical requests without giving clinical advice.

The reusable Python core powers a CLI and Marimo Lab UI. Genuine OpenAI interpretation extracts bounded intent and fields; deterministic code and a ZEN policy gate retain authority over identity, API facts, consent and effects. Rehearsal mode remains available without credentials. The supplied scheduling service is an unchanged local mock; all fixtures are synthetic.

The accepted stories and success criteria live in the [feature specification](../../specs/001-appointment-assistant/spec.md). [Tasks and qualification](../../specs/001-appointment-assistant/tasks.md) record implemented outcomes, including fresh Mac ARM and Linux checks. [Personas](personas.md) remain unresolved placeholders rather than claimed user validation.

Unknown write outcomes stop automatic retries and require reconciliation. The product has no production authentication, durable transaction guarantee or clinical/compliance certification. Actual walkthrough video, named Persona validation and external delivery remain in [next steps](next-steps.md).
