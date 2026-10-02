#!/usr/bin/env python3
"""Fail when README.md's stated row count or head hash drifts from the ledger.

    python3 tools/check_readme.py

The README quotes `verify_chain.py`'s output. When a row is appended the quote
goes stale silently — it did between 17884ae (a fourth row) and 2026-10-02,
while the README still said three rows and the old head. This reads the real
verifier's output and the README's quote and refuses to let them differ.
Stdlib only; exit 0 agree, 1 drift, 2 could not check.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "verify_chain.py"),
                        str(ROOT / "ledger.jsonl")], capture_output=True, text=True, timeout=60)
    m = re.search(r"OK: (\d+) row\(s\) verified\. Ledger head hash: ([0-9a-f]{64})", r.stdout)
    if r.returncode != 0 or not m:
        print(f"REFUSE: verify_chain.py did not report a head:\n{r.stdout}{r.stderr}", file=sys.stderr)
        return 2
    rows, head = int(m.group(1)), m.group(2)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    q = re.search(r"OK: (\d+) row\(s\) verified\. Ledger head hash: ([0-9a-f]{64})", readme)
    if not q:
        print("REFUSE: README.md no longer quotes the verifier's output", file=sys.stderr)
        return 2
    words = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six"}
    problems = []
    if int(q.group(1)) != rows:
        problems.append(f"README quotes {q.group(1)} rows; the ledger has {rows}")
    if q.group(2) != head:
        problems.append(f"README quotes head {q.group(2)[:16]}…; the ledger's is {head[:16]}…")
    if f"| `ledger.jsonl` | {words.get(rows, rows)} synthetic rows" not in readme:
        problems.append(f"the layout table does not say '{words.get(rows, rows)} synthetic rows'")
    if problems:
        print("README drift:\n  " + "\n  ".join(problems))
        return 1
    print(f"OK: README agrees with the ledger ({rows} rows, head {head[:16]}…)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
