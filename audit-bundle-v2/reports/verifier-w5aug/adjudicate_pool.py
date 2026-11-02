#!/usr/bin/env python3
"""adjudicate_pool.py - verifier-w5aug: every dumped pool BAD line
decided by myref.py; the file-want side must match in all 604678.
Classifies kernel-got deviation shapes per kind. Usage:
  adjudicate_pool.py <pool-bad.log>"""
import re
import sys

sys.path.insert(0, sys.path[0])
from myref import ref

OPN = {"0": "add", "1": "sub", "2": "mul"}
want_bad = {}
got_shapes = {}
n = 0
with open(sys.argv[1], encoding="utf-8", errors="replace") as f:
    for ln in f:
        if not ln.startswith("BAD"):
            continue
        m = re.match(r"BAD op=(\d) a=([0-9a-f]+) b=([0-9a-f]+) got (\S+) (\S+)/(\S+) want (\S+) (\S+)/(\S+) kind=(\S+)", ln)
        op, a, b, gh, gt, gf, wh, wt, wf, kind = m.groups()
        op, a, b = OPN[op], int(a, 16), int(b, 16)
        eh, et, ef = ref("f16", op, a, b)
        if (wh, wt, int(wf, 16)) != ("%04x" % eh, "%04x" % et, ef):
            want_bad[(op, a, b)] = (ln.strip(), eh, et, ef)
        s = ("H" if gh != wh else "") + ("T" if gt != wt else "") + ("F" if gf != wf else "")
        k = (kind, s, op)
        got_shapes[k] = got_shapes.get(k, 0) + 1
        n += 1
print("adjudicated:", n)
print("want!=myref:", len(want_bad))
for k in sorted(got_shapes):
    print(k, got_shapes[k])
for v in list(want_bad.values())[:10]:
    print("WANT-BAD:", v)
