# queue/

One state file per task (see `SCHEMA.md`). In a live ledger, leases and
`MERGE_LOCK.json` also live here as appends, and a lapsed lease returns its task
with an `ABANDONED` ledger row.

This reference ledger carries a single task, `T-0001`, parked in `IN_REVIEW` with
`approve_role: code_review` — the state `dx merge` expects to gate.
