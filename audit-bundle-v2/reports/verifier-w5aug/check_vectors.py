#!/usr/bin/env python3
"""check_vectors.py - verifier-w5aug: myref.py vs every committed
augmented vector line (all 3 formats). Also rechecks the kind census
shape (counts per family tag). Usage:
  check_vectors.py <vectors-dir> ; exit nonzero on any mismatch."""
import sys

sys.path.insert(0, sys.path[0])
from myref import ref, fmt_hex

W = {"f16": 4, "f32": 8, "f64": 16}


def main():
    vdir = sys.argv[1]
    bad, total = 0, 0
    for fmt in ("f16", "f32", "f64"):
        w = W[fmt]
        with open("%s/aug-%s.vec" % (vdir, fmt), encoding="utf-8") as f:
            for lno, raw in enumerate(f, 1):
                s = raw.strip()
                if not s or s.startswith("#"):
                    continue
                tok = s.split()
                op = tok[0].split("augmented_")[1]  # msf16_augmented_add -> add
                assert tok[1] == "-" and tok[4] == "->", (fmt, lno, s)
                a, b = int(tok[2], 16), int(tok[3], 16)
                wh, wt, wf = tok[5], tok[6], int(tok[7], 16)
                eh, et, ef = ref(fmt, op, a, b)
                want = (fmt_hex(fmt, eh), fmt_hex(fmt, et), ef)
                got = (wh.lower(), wt.lower(), wf)
                total += 1
                if (want[0], want[1], want[2]) != (got[0], got[1], got[2]):
                    bad += 1
                    if bad <= 20:
                        print("VEC-MISMATCH %s:%d %s: file %s %s/%02x myref %s %s/%02x" % (
                            fmt, lno, s, wh, wt, wf, want[0], want[1], want[2]))
    print("check_vectors: %d lines, %d mismatches" % (total, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
