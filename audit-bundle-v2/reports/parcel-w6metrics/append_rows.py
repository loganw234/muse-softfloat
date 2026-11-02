#!/usr/bin/env python3
"""Append new-*.jsonl rows to the worktree metrics files (append-only).

One process; single append-mode handle per file; proves the frozen prefix
is byte-identical afterwards and the result equals the pre-validated
combined-check copies byte for byte.
"""
import hashlib
from pathlib import Path

WS = Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
DST = WS / "worktrees/w6-metrics/docs/metrics"
HERE = Path(__file__).parent

for name in ("usage", "passes", "escalations", "briefs"):
    dst = DST / f"{name}.jsonl"
    before = dst.read_bytes()
    assert before.endswith(b"\n"), name
    new = (HERE / f"new-{name}.jsonl").read_bytes()
    with open(dst, "ab") as f:
        f.write(new)
    after = dst.read_bytes()
    ok_prefix = after[: len(before)] == before
    combined = (HERE / "combined-check" / f"{name}.jsonl").read_bytes()
    ok_combined = after == combined
    n0 = before.decode("utf-8").count("\n")
    n1 = after.decode("utf-8").count("\n")
    print(f"{name}: rows {n0} -> {n1} (+{n1-n0}); frozen prefix identical={ok_prefix}; "
          f"equals pre-validated combined={ok_combined}; "
          f"prefix sha256 {hashlib.sha256(before).hexdigest()[:16]}; file sha256 {hashlib.sha256(after).hexdigest()[:16]}")
    assert ok_prefix and ok_combined and after[len(before):] == new
print("append ok")
