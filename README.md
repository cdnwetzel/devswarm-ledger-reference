# devswarm-ledger-reference

A **reference implementation** of the append-only, hash-chained approval ledger
that [`dx-orchestrator`](https://github.com/cdnwetzel/dx-orchestrator) gates
merges against.

> **Every row here is synthetic and attests to no real work.** This repository
> exists so `dx merge` can be run end-to-end without a private operational
> ledger. The chain rules, canonical form, signature payload and key standard are
> the real ones; only the contents are invented.

## Why this exists separately

A live ledger is operational state, not a library. It is append-only by rule
(RL-009), so publishing one is a commitment to publish every future task event
forever — and it cannot be redacted after the fact, because editing any row
breaks every subsequent hash and invalidates every signature bound to the head.

So the format is published and the operational history is not. `dx` needs only
the format: it delegates chain verification to `tools/verify_chain.py` and reads
`queue/<task>.json`, `approvals/*.asc` and `docs/keys/`.

## Layout

| Path | What it is |
| --- | --- |
| `ledger.jsonl` | Three synthetic rows with their own genesis, in canonical form |
| `queue/T-0001.json` | One task in `IN_REVIEW`, `approve_role: code_review` |
| `approvals/T-0001.code_review.{asc,msg}` | A real GPG detached signature over the real head |
| `docs/keys/reviewer.asc` | The demo signer's **public** key |
| `tools/verify_chain.py` | The chain verifier — stdlib only, no dependencies |
| `tools/new_demo_approval.sh` | Regenerate a demo key and re-sign after extending the ledger |
| `SCHEMA.md` | Field definitions, canonical form, chain rule, correction convention |

## Verify it

```
$ python3 tools/verify_chain.py ledger.jsonl
OK: 3 row(s) verified. Ledger head hash: b8b8baca959ddfbe049f6703a2ed687211eaed4ad36f2c62ddd38df85be231f4
```

## Run the gate

```
$ DX_LEDGER_REPO=$PWD dx merge T-0001
✅ Ledger chain verifies. Head: b8b8baca959ddfbe…
✅ Signature verified. Signer: Rex Reviewer <reviewer@example.invalid>
✅ Signed message binds task_id + current head + role.
✅ Separation of duties: author 'Ada Author' ≠ signer 'Rex Reviewer'.
✅ All RL-003 checks passed for T-0001.
```

Four gates, and each one can fail independently.

## Watch it fail — this is the part that matters

A fixture that only ever passes proves nothing. Append one row, so the head moves
away from what the signature binds to:

```
$ DX_LEDGER_REPO=$PWD dx merge T-0001
✅ Ledger chain verifies. Head: ed127b72ca5642a3…
✅ Signature verified. Signer: Rex Reviewer <reviewer@example.invalid>
❌ Stale signature (RL-003). Signed head b8b8baca959ddfbe… but current head is
   ed127b72ca5642a3…. Re-sign after re-verifying the chain.
exit 1
```

The signature is still cryptographically valid — note gate 2 passes. It is
*stale*, and staleness is the whole point of binding an approval to a head hash:
approve this exact state of the world, not "this task, whenever". Extend the
ledger and re-sign with `tools/new_demo_approval.sh`.

The other gates fail independently too, each verified:

| Tamper with | Result |
| --- | --- |
| Remove `docs/keys/reviewer.asc` | `NO_PUBKEY` — the signer is not registered, so the signature is not evidence |
| Edit `approvals/T-0001.code_review.msg` | `BADSIG` — the signature covers that file, so any edit invalidates it |
| Set the ledger's `author_human` to `Rex Reviewer` | `❌ Separation-of-duties violation: author 'Rex Reviewer' and signer 'Rex Reviewer' are the same person.` |

Note what the second row means: you cannot reach the payload-binding gate by
editing the message, because editing it breaks the signature first. That gate
exists for a different adversary — someone who *can* sign, signing something
other than `task_id + head + role`. Defence in depth, not redundancy.

## About the demo key

`reviewer.asc` is a demo key and its uid says so. It was generated
non-interactively, unprotected, by a script — **the exact opposite of the RL-010
standard in `docs/keys/README.md`**, which governs real approval keys. (RL-010 was
amended — charter Decision 0017 — to a hardware-resident, non-exportable key; it
still preserves a *marked* software fallback, and this demo key is the opposite of
even that.)

Its private half was never committed and no longer exists; it was destroyed with
the temporary keyring that produced it. Verification does not need it. A
reference implementation that shipped a private signing key would contradict the
standard it is meant to teach, and "the agent cannot produce this signature" is
the load-bearing claim of the entire approval design.

## Licence

MIT — see [LICENSE](LICENSE).
