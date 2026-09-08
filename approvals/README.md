# approvals/

GPG **detached** signatures over the canonical string
`task_id + ledger_head_hash + role` — exact concatenation, no separators, UTF-8 —
named `<task_id>.<role>.asc` with the signed payload alongside as `.msg`.

A signature over a stale head is invalid (RL-003). That is not an edge case to
work around; it is the mechanism. Append one row to `ledger.jsonl` and
`T-0001.code_review.asc` becomes correctly unverifiable — see the transcript in
the top-level `README.md`.
