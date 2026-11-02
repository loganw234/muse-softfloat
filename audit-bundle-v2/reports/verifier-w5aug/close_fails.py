#!/usr/bin/env python3
"""close_fails.py - verifier-w5aug: for every runner FAIL line over the
committed aug vectors, decide the case with myref.py and report which
side (kernel-got or file-want) matches the clause reference.
Usage: close_fails.py <runner-log-utf16> <vectors-dir>"""
import re
import sys

sys.path.insert(0, sys.path[0])
from myref import ref

txt = open(sys.argv[1], encoding="utf-16", errors="replace").read()
vdir = sys.argv[2]
fails = [l for l in txt.splitlines() if l.startswith("FAIL")]
W = {"msf16": ("f16", 4), "msf32": ("f32", 8), "msf64": ("f64", 16)}
n_got_ok = n_want_ok = n_neither = 0
want_ok_ex = []
for l in fails:
    m = re.match(r"FAIL (\S+):(\d+) got (\S+) (\S+)/(\S+) want (\S+) (\S+)/(\S+) \| (\S+) - (\S+) (\S+) ->", l)
    if not m:
        print("UNPARSED:", l[:160])
        continue
    _f, _ln, gh, gt, gf, wh, wt, wf, opname, a, b = m.groups()
    tag = opname[:5]
    fmt, w = W[tag]
    op = opname.split("augmented_")[1]
    a, b = int(a, 16), int(b, 16)
    eh, et, ef = ref(fmt, op, a, b)
    ref3 = ("%0*x" % (w, eh), "%0*x" % (w, et), ef)
    # runner prints full 16-hex-digit zero-padded words; mask to width
    got3 = (gh[-w:].lower(), gt[-w:].lower(), int(gf, 16))
    want3 = (wh[-w:].lower(), wt[-w:].lower(), int(wf, 16))
    got_ok, want_ok = got3 == ref3, want3 == ref3
    if got_ok and not want_ok:
        n_got_ok += 1
        want_ok_ex.append((_f, _ln, l[:200]))
    elif want_ok and not got_ok:
        n_want_ok += 1
    else:
        n_neither += 1
        print("NEITHER:", l[:220])
print("fails:", len(fails), "kernel-right:", n_got_ok, "file-right:", n_want_ok,
      "neither:", n_neither)
for e in want_ok_ex[:10]:
    print("KERNEL-RIGHT:", e)
