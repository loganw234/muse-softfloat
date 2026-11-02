#!/usr/bin/env python3
"""Binary16 exhaustive trig relabel stream (scratch gate):
every f16 encoding x sinPi/cosPi, expectation = decider te
result relabeled ta (Niven: no exact ties)."""
import os
import subprocess
import sys

exe = sys.argv[1]
outpath = sys.argv[2]
jobs = []
for fn in ("sin_pi", "cos_pi"):
    for x in range(65536):
        jobs.append((f"msf16_{fn}", x))
inp = "".join(f"{op} {x:x}\n" for op, x in jobs)
proc = subprocess.run([exe, "decide"], input=inp,
                      capture_output=True, text=True)
if proc.returncode != 0:
    sys.stdout.write(proc.stdout[-2000:])
    print("decider failed rc=%d" % proc.returncode, file=sys.stderr)
    sys.exit(1)
decided = {}
for line in proc.stdout.splitlines():
    t = line.split()
    if len(t) == 10:
        decided[(t[0], t[1])] = (t[2], t[3])  # te bits, flags
print("decided %d of %d" % (len(decided), len(jobs)))
if len(decided) != len(jobs):
    sys.exit(1)
with open(outpath, "w", newline="\n", encoding="utf-8") as fh:
    fh.write("# scratch gate: f16 exhaustive sinPi/cosPi, te "
             "expectations relabeled ta (Niven)\n")
    for op, x in jobs:
        rb, rf = decided[(op, f"{x:x}")]
        fh.write(f"{op} ta {x:x} -> {rb} {rf} "
                 f"mpfr640-trig:f16exh-ta-relabel\n")
print("wrote", outpath)
