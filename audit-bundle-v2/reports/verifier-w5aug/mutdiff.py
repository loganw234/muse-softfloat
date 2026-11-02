#!/usr/bin/env python3
"""mutdiff.py - verifier-w5aug: run the onecells case list through the
shipped probe and each mutant probe; report per-mutant diff counts
vs shipped (proves TE_HEAD is a no-op and the others are live)."""
import subprocess
import sys

sys.path.insert(0, sys.path[0])
from onecells import cases
from myref import fmt_hex


def run(probe, cs):
    inp = "".join("%s %s %s %s\n" % (f, o, fmt_hex(f, a), fmt_hex(f, b))
                  for _, f, o, a, b in cs)
    p = subprocess.run([probe], input=inp, capture_output=True, text=True)
    return p.stdout.strip().split("\n")


def main():
    d = sys.argv[1]  # build dir
    cs = cases()
    base = run(d + "/probe_aug.exe", cs)
    print("cases:", len(cs))
    for m in ("TE_HEAD", "ZERO_TAIL_SIGN", "SWAP_PAIR", "JAM_WINDOW",
              "P1_OPPOSITE", "PACK_LEAK"):
        out = run(d + "/probe_%s.exe" % m, cs)
        ndiff = sum(1 for x, y in zip(base, out) if x != y)
        print("mutant %-14s diffs-vs-shipped: %d" % (m, ndiff))
        shown = 0
        for (lab, f, o, a, b), x, y in zip(cs, base, out):
            if x != y and shown < 3:
                print("   %s %s %s: shipped %s mutant %s" % (lab, fmt_hex(f, a), fmt_hex(f, b), x, y))
                shown += 1


if __name__ == "__main__":
    main()
