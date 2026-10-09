# Third-party notices and supplied reference provenance

Updated: 2026-10-08 (America/Chicago).

## Reasoning Lab patterns

The standalone submission-generation gate and safe event projection design are inspired by nxus.SYSTEMS LLC's public nxusKit examples. This candidate does not require or vendor the nxusKit SDK or the full example repository. Specific implementation attribution should be retained with any adapted portions.

Pinned public source revision: `fd801bbc548e88fb5858e924089f3753fe7b0650`.

- [Safe event emitter](https://github.com/nxus-SYSTEMS/nxusKit-examples/blob/fd801bbc548e88fb5858e924089f3753fe7b0650/examples/integrations/common-sense-guardrails/python/run_events.py), SHA-256 `f88844f6177f34d90a646cb30a3c252f745585dee8908e9453e30c9899e06cc1`.
- [AnalysisSubmissionGate](https://github.com/nxus-SYSTEMS/nxusKit-examples/blob/fd801bbc548e88fb5858e924089f3753fe7b0650/examples/integrations/common-sense-guardrails/marimo/frontend_core.py), SHA-256 `2c42f28170b0eeb232a0b55684bfb4adb4e0906ef7ff1edeb44824fc6c2090f9`.

The repository offers MIT or Apache-2.0 at the recipient's option. MIT is selected for any adapted portions. Copyright (c) 2026 nxus.SYSTEMS LLC. The complete notice is retained in [licenses/nxusKit-examples-MIT.txt](licenses/nxusKit-examples-MIT.txt), SHA-256 `8400a8ace99460c4accd5a6c07677b95aaf01a672a85f30132aec8022a5b51b6`.

Public pinned bytes were fetched and compared against the inspected local examples; both referenced files and the MIT license matched. No private-only source is copied. The original interaction inspector's raw messages/responses are not appropriate evidence for this scheduling application; the candidate's evidence projection must omit sensitive content.

## Supplied assignment reference API

`vendor/reference-api/` contains only the unchanged supplied `mock-api/server.py`, its README, synthetic `data/*.json` and README, and `openapi/scheduling-api.yaml`. Their sibling directory layout is preserved so the supplied server reads its fixtures normally. Origin: the Operator-supplied patient appointment assignment package, inspected 2026-10-08. The data README identifies every record as fabricated; no real patient data is included.

This is private reviewer-clone packaging under the Operator's assignment grant. No separate open-source license was supplied for this subset; no general redistribution permission is asserted. The full intake, invitation/email, metadata and credentials are excluded. Restarting each candidate's separate mock server resets its in-memory booking state.

| Supplied file | SHA-256 of unchanged bytes |
| --- | --- |
| `vendor/reference-api/data/README.md` | `be5b3dc7289a97838316f0f203bc6adae1d63bedce771e68555cfa8c55aab356` |
| `vendor/reference-api/data/appointments.json` | `02be083e7d1d5841b29a4bb1fb663ba49f6c3d9ed47c236fa67545e8432d0d65` |
| `vendor/reference-api/data/patients.json` | `4bc471bef84eccee513b2ae15127cbf532b6aa47f151831ff7c2a6b832889d48` |
| `vendor/reference-api/data/providers.json` | `0745b592a15821474ebee45f868c3ed90d4bf24846903a17e7da0b210a3d92d6` |
| `vendor/reference-api/data/slots.json` | `340bb75c9c737281de2e48b7c299141ce4c27e41001c0172c4e8f0927cf0ce9b` |
| `vendor/reference-api/mock-api/README.md` | `b7d463b52e61cbf63cb0d70ebe661eea67b25332e4af19ff2b86ae239cafde80` |
| `vendor/reference-api/mock-api/server.py` | `9597f92fe3ec19c16e08b1491fbac12e1ffed87bd41c137be1e638addac2d1f1` |
| `vendor/reference-api/openapi/scheduling-api.yaml` | `62e17d269d924d1a3832c16a262cb85f78ebbceb078cdb73e759a91bf40fa735` |

## UI assets

Approved Ochsner logo and project-owned theme tokens are indexed in [docs/internal/ui-assets.md](docs/internal/ui-assets.md). Logo use is authorized for the Ochsner-internal audience only; it does not imply sponsor certification or general public redistribution rights.
