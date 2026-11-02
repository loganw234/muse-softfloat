#!/usr/bin/env python3
"""s08b_jam_truth.py - JAM build vs fastdec on the s02 pair files."""
import subprocess
import sys
import os

OUT = "scratch/verifier-w5alg2/out"
JAM = OUT + "/harness_jam.exe"
FASTDEC = "scratch/verifier-w5alg2/fastdec.py"
PY = os.environ.get("MSF_PYTHON", "python")

for fn, fi in (("s02_f16_hypot_pairs.txt", 0),
               ("s02_f32_hypot_pairs.txt", 1),
               ("s02_f64_hypot_pairs.txt", 2)):
    blob = open(f"{OUT}/{fn}").read()
    kj = subprocess.run([JAM, "hypot"], input=blob, capture_output=True,
                        text=True)
    fd = subprocess.run([PY, FASTDEC], input=blob, capture_output=True,
                        text=True)
    if kj.returncode != 0 or fd.returncode != 0:
        raise RuntimeError("harness failed")
    mm = tot = 0
    first = []
    for kl, fl in zip(kj.stdout.splitlines(), fd.stdout.splitlines()):
        kt, ft = kl.split(), fl.split()
        for i in range(5):
            lb, lf = int(kt[2 * i], 16), int(kt[2 * i + 1], 16)
            rb, rf = int(ft[2 * i], 16), int(ft[2 * i + 1], 16)
            tot += 1
            if (lb, lf) != (rb, rf):
                mm += 1
                if len(first) < 3:
                    first.append((i, kl, fl))
    print(f"JAM-vs-MYDEC fi={fi}: decisions={tot} mismatches={mm} "
          f"{'PASS' if mm == 0 else 'FAIL'}", flush=True)
    for i, kl, fl in first:
        print(f"  rm={i} jam='{kl}' mine='{fl}'", flush=True)
