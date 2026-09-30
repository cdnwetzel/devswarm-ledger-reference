# devswarm-ledger — schema and chain rules

> The append-only, hash-chained ledger format used by `dx merge` for RL-003
> approval gating. The red lines quoted below come from a private operational
> charter; they are reproduced here because the format cannot be understood
> without them, and they are the whole reason the format looks like this:
> **RL-008** (agents never write to the ledger), **RL-009** (append-only, no
> history rewrite — corrections are appended rows referencing the erroneous row
> by hash), **RL-011** (every evidence write passes a redaction filter at capture
> time; the store never holds a live secret), **RL-010** (approval keys are
> hardware-resident and non-exportable, and every signature needs a physical
> gesture — the harness can never hold the private half).

> The shared control-plane state for DevSwarmX. Governed by the charter at `github.com/cdnwetzel/DevSwarmX`: **RL-008** (agents never write here), **RL-009** (append-only, no history rewrite — corrections are appended rows referencing the erroneous row by hash), **RL-011** (every evidence write passes the redaction filter at capture time; this store never holds a live secret), **RL-010** (approval keys are hardware-resident and non-exportable, and every signature needs a physical gesture — the harness can never hold the private half).

## `ledger.jsonl`

One JSON object per line, append-only, hash-chained.

**Fields:** `ts` (ISO 8601 UTC) · `task_id` · `author_seat` · `author_human` · `reviewer_seat` · `action` (`GENESIS | ADMITTED | EXECUTED | EVIDENCE | REVIEWED | SIGNED | MERGED | INCOMPLETE | ABANDONED | ESCALATED | REDLINE | CORRECTION`) · `sha` (relevant git commit) · `evidence` (redacted — RL-011) · `prev_hash`.

**Canonical form** of a row: `json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True)` — key-sorted, no whitespace, ASCII-escaped. Deterministic across machines.

**Chain rule:** a row's hash is `sha256(canonical_form)` (the `prev_hash` field included). Row N's `prev_hash` must equal row N−1's hash. The genesis row's `prev_hash` is 64 zeros. The **ledger head hash** is the hash of the last row — this is the value approval signatures bind to.

**Evidence conventions** (no new fields; `evidence` carries `key=value` pairs the way `mode=BRIDGE` does): on `SIGNED` and `MERGED` rows the merge gate writes `approval_tier=<single-reviewer|two-human>`, `mechanism=<hardware (RL-010: non-exportable key, gesture per signature) | fallback (RL-010 non-compliant: software key)>` derived from `docs/keys/REGISTRY.json` (never supplied by the signer or a flag), and, when the author signed on a single-reviewer scope, `sod_exception=author≠reviewer (author signed; scope single-reviewer)` (charter Decision 0020). On `EXECUTED` rows the runner writes provenance when it knows it: `run=<run id> model=<resolved model> pxx=<version> identity=<psguard identity>`.

**Corrections:** a wrong row is never edited or deleted (RL-009). Append an `action: "CORRECTION"` row whose `evidence` names the erroneous row's hash and states the correction. The error stays visible; that is the point.

Verify any copy with `python3 tools/verify_chain.py` — exit 0 and a head hash, or a stop-the-line failure. A broken chain is a kill condition, not a recoverable error.

## `queue/`

One state file per task, named `<task_id>.json`, holding the current state: `ADMITTED → IN_PROGRESS → EVIDENCE_POSTED → IN_REVIEW → APPROVED → MERGED` (or `INCOMPLETE` / `ESCALATED`), plus lease fields (`lease_seat`, `lease_row_hash`). Lease expiry is judged against ledger commit timestamps, never a dispatcher's clock; a lapsed lease returns the task with an `ABANDONED` ledger row. `MERGE_LOCK.json` serializes merges: acquiring it is an append, and two concurrent claims collide as a git conflict — the loser backs off.

## `approvals/`

GPG **detached** signatures over the canonical string `task_id + ledger_head_hash + role` (exact concatenation, no separators, UTF-8). Named `<task_id>.<role>.asc`. Valid only if: the key belongs to the human accountable for that role (public keys in `docs/keys/`), the signer is not the change's author where an invariant requires separation, and the signed head hash is the **current** head (a stale-head signature is invalid — RL-003).

## `docs/keys/`

`REGISTRY.json` lists every key file here with `fingerprint`, `holder` (the bare uid name, equal to `author_human`), `residency` (`card` | `software`), `registered` and `retired`. The verifier imports only listed, unretired keys; a file it does not list does not verify. A retired file stays so past signatures verify by hand.

Each member's public signing key, `<name>.asc`. The private keys are **hardware-resident and non-exportable** to the RL-010 standard (amended — charter Decision 0017): they live on a CCID OpenPGP token, every signature needs a physical gesture, and they are a **different key** from the one backing `pass`/age. Until a token is present, the original interactive software ceremony is the marked fallback, and every row it signs records `mechanism` as fallback.
