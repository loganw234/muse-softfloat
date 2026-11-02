#!/usr/bin/env python3
"""Append new-*.jsonl rows to the worktree metrics files (append-only).

One process per run; writes with a single append-mode handle per file and
proves the frozen prefix is byte-identical afterwards.
"""
import hashlib
from pathlib import Path

WS = Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
DST = WS / "worktrees/w5-metrics/docs/metrics"
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
    n0 = before.decode("utf-8").count("\n")
    n1 = after.decode("utf-8").count("\n")
    print(f"{name}: rows {n0} -> {n1} (+{n1-n0}); frozen prefix identical={ok_prefix}; "
          f"prefix sha256 {hashlib.sha256(before).hexdigest()[:16]}; file sha256 {hashlib.sha256(after).hexdigest()[:16]}")
    assert ok_prefix and after[len(before):] == new
print("append ok")
