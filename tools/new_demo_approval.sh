#!/usr/bin/env bash
# new_demo_approval.sh — re-sign the approval after extending the ledger.
#
# The shipped signature binds to the shipped head. Append any row and it goes
# stale (correctly — RL-003). This regenerates a demo key of your own, registers
# its public half, and signs the CURRENT head.
#
# Usage: ./tools/new_demo_approval.sh [task_id] [role]
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TASK="${1:-T-0001}"; ROLE="${2:-code_review}"
NAME="${DEMO_SIGNER_NAME:-Rex Reviewer}"
EMAIL="${DEMO_SIGNER_EMAIL:-reviewer@example.invalid}"

GNUPGHOME="$(mktemp -d)"; export GNUPGHOME; chmod 700 "$GNUPGHOME"
trap 'rm -rf "$GNUPGHOME"' EXIT
gpg --batch --gen-key >/dev/null 2>&1 <<EOF
%no-protection
Key-Type: eddsa
Key-Curve: Ed25519
Key-Usage: sign
Name-Real: ${NAME}
Name-Comment: reference ledger DEMO key - not for real approvals
Name-Email: ${EMAIL}
Expire-Date: 0
%commit
EOF
gpg --armor --export "$EMAIL" > "$REPO/docs/keys/reviewer.asc"

HEAD="$(python3 "$REPO/tools/verify_chain.py" "$REPO/ledger.jsonl" | sed 's/.*head hash: //')"
printf '%s' "${TASK}${HEAD}${ROLE}" > "$REPO/approvals/${TASK}.${ROLE}.msg"
gpg --armor --detach-sign --output "$REPO/approvals/${TASK}.${ROLE}.asc" \
    --yes "$REPO/approvals/${TASK}.${ROLE}.msg"
echo "Re-signed ${TASK}.${ROLE} against head ${HEAD}"
echo "The private key was destroyed with the temp keyring; only the public half is registered."
