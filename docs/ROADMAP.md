# devswarm-ledger-reference roadmap

Open items that are not yet decided or done.

## Open

_None tracked yet._ Add an item here (what, why, owner, status) before
starting work that spans releases.

## Cross-repo alignment

dx-orchestrator's CI clones this repo and reads its ledger schema and
admission rules (see [`SCHEMA.md`](../SCHEMA.md)). The `pxx=<version>`
provenance field is free text. A schema change must be checked against dx's
suite before it lands.
