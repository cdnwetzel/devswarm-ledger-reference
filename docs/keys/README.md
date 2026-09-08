# Signing keys (RL-010 standard)

Each member's **public** approval-signing key lives here as `<name>.asc`. The private keys never do — and never touch the harness.

Generating yours (each member, **by hand, in a plain terminal — never via an agent session**):

```sh
gpg --full-generate-key          # ECC (sign only) → Curve 25519; real passphrase typed at the pinentry
gpg --list-secret-keys --keyid-format long   # find YOUR_KEYID
gpg --armor --export YOUR_KEYID > docs/keys/<name>.asc
git add docs/keys/<name>.asc && git commit -m "Add <seat> public key" && git push
```

The RL-010 standard, in full:
- Generated **interactively by the accountable person** — never non-interactively, never by an agent.
- The passphrase is never stored in a file, env var, script, or `pass` store — nowhere a runner or agent slot can read.
- A **different key** (not a subkey of the same primary) from the one backing `pass`/age secret decryption.
- No long-lived `gpg-agent` caching on any box that runs agent slots (keep `default-cache-ttl`/`max-cache-ttl` short in `~/.gnupg/gpg-agent.conf`, e.g. ≤ 300 s).

A gate an agent can satisfy is not a gate. The whole approval structure (RL-003) reduces to "the agent cannot produce this signature" — this directory's discipline is what makes that true.

---

## The demo key in this reference ledger

`reviewer.asc` is a **demo** public key — "Rex Reviewer (dx reference ledger DEMO
key — not for real approvals)". It exists so `dx merge` can be run end-to-end by
anyone. It is **not** an RL-010 key and nothing above was followed in making it:
it was generated non-interactively, unprotected, by a script.

Its private half was never committed and no longer exists — it was destroyed with
the temporary keyring that made it. That is deliberate. A reference
implementation that shipped a private signing key would contradict this document
in the very directory the document governs, and "the agent cannot produce this
signature" is the whole load-bearing claim of RL-003.

Verification never needs the private half. If you extend the ledger and need to
re-sign, `tools/new_demo_approval.sh` generates a fresh demo key of your own,
registers its public half here, and signs the current head.
