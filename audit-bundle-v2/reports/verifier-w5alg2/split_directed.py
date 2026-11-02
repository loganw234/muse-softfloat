#!/usr/bin/env python3
"""split_directed.py - classify s09 directed kernel-mm lines."""
import subprocess
import os

OUT = "scratch/verifier-w5alg2/out"
EXE = OUT + "/harness_floor.exe"

for fi, fn in ((1, "worktrees/verify5-alg2/tests/vectors/alg-f32.vec"),
               (2, "worktrees/verify5-alg2/tests/vectors/alg-f64.vec")):
    w = 32 if fi == 1 else 64
    jobs = []
    for line in open(fn):
        t = line.split()
        if len(t) >= 8 and "hypot" in t[0] and t[7] == "mpfr-alg:directed":
            jobs.append((t[1], int(t[2], 16), int(t[3], 16), int(t[5], 16),
                         int(t[6], 16)))
    blob = "".join(f"{fi} {a:x} {b:x}\n" for _, a, b, _, _ in jobs)
    kh = subprocess.run([EXE, "hypot"], input=blob, capture_output=True,
                        text=True)
    from collections import Counter
    c = Counter()
    for (rm, a, b, rb, rf), line in zip(jobs, kh.stdout.splitlines()):
        kt = line.split()
        i = {"te": 0, "tz": 1, "tp": 2, "tn": 3, "ta": 4}[rm]
        kb, kf = int(kt[2 * i], 16), int(kt[2 * i + 1], 16)
        if (kb, kf) != (rb, rf):
            z = a in (0, 1 << (w - 1)) and b in (0, 1 << (w - 1))
            c["zero" if z else ("bits" if kb != rb else "flags")] += 1
    print(f"fi={fi} directed kernel-mm split: {dict(c)}")
