#!/usr/bin/env python3
"""DevSwarmX ledger chain verifier.

Ships with the schema (Gate 0, PLAN.md): a ledger you cannot verify is not
evidence. Verifies that every row of ledger.jsonl chains to its parent by
sha256 over the canonical JSON form, and prints the head hash — the value
approval signatures bind to (RL-003).

Exit 0: chain verifies; head hash printed.
Exit 1: chain broken / malformed — a stop-the-line kill condition (RL-009).

Usage: python3 tools/verify_chain.py [path/to/ledger.jsonl]
"""
import hashlib
import json
import sys
from pathlib import Path

GENESIS_PREV = "0" * 64


def canonical(row: dict) -> str:
    return json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def row_hash(row: dict) -> str:
    return hashlib.sha256(canonical(row).encode("utf-8")).hexdigest()


def fail(line_no: int, msg: str) -> None:
    print(f"CHAIN BROKEN at row {line_no}: {msg}", file=sys.stderr)
    print("Stop the line (RL-009). Every downstream signature is suspect until "
          "the chain re-verifies against a trusted copy.", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "ledger.jsonl"
    if not path.exists():
        print(f"No ledger at {path}", file=sys.stderr)
        sys.exit(1)

    prev = GENESIS_PREV
    rows = 0
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line.strip():
                fail(line_no, "blank line in an append-only log")
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                fail(line_no, f"not valid JSON ({e})")
            if not isinstance(row, dict):
                fail(line_no, "row is not a JSON object")
            got = row.get("prev_hash")
            if got != prev:
                fail(line_no, f"prev_hash mismatch — expected {prev}, got {got}")
            if canonical(row) != line:
                fail(line_no, "row is not in canonical form (sorted keys, compact separators, ascii)")
            prev = row_hash(row)
            rows += 1

    if rows == 0:
        fail(0, "ledger is empty — even a fresh ledger has its genesis row")
    print(f"OK: {rows} row(s) verified. Ledger head hash: {prev}")


if __name__ == "__main__":
    main()
