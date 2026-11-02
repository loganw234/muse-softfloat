#!/usr/bin/env python3
"""s08_jam_kernel.py - shipped floor build vs MSF_ALG_TEST_JAM build.

Same inputs through both kernel binaries; counts packed divergences
(bits+flags x5). Inputs: full f16 pool sweep (1,310,720 pairs),
200k seeded f32, 200k seeded f64, directed pools. No truth oracle
here: this measures whether the two shipped/test forms can diverge.
"""
import random
import subprocess
import sys
import os

OUT = "scratch/verifier-w5alg2/out"
FLOOR = OUT + "/harness_floor.exe"
JAM = OUT + "/harness_jam.exe"
POOL = [0x0000, 0x8000, 0x0001, 0x8001, 0x0002, 0x03ff, 0x0400,
        0x3c00, 0xbc00, 0x3555, 0x7bff, 0x7c00, 0xfc00, 0x7e00,
        0xfe00, 0x7d55, 0x7c01, 0xfc01, 0x0003, 0x03fd]


def run_both(fi, gen):
    mm = tot = 0
    first = []
    nk = 0
    blob = []
    for a, b in gen:
        blob.append(f"{fi} {a:x} {b:x}\n")
        if len(blob) >= 65536:
            m, t, f = cmp_blob(fi, blob)
            mm += m
            tot += t
            first += f
            nk += 1
            blob = []
            print(f"  fi={fi} chunk {nk}: cum_mm={mm}", flush=True)
    if blob:
        m, t, f = cmp_blob(fi, blob)
        mm += m
        tot += t
        first += f
    return mm, tot, first[:5]


def cmp_blob(fi, blob):
    s = "".join(blob)
    kf = subprocess.run([FLOOR, "hypot"], input=s, capture_output=True,
                        text=True)
    kj = subprocess.run([JAM, "hypot"], input=s, capture_output=True,
                        text=True)
    if kf.returncode != 0 or kj.returncode != 0:
        raise RuntimeError("harness failed")
    lf, lj = kf.stdout.splitlines(), kj.stdout.splitlines()
    assert len(lf) == len(lj) == len(blob)
    mm = tot = 0
    first = []
    for (inp, a, c) in zip(blob, lf, lj):
        ft, jt = a.split(), c.split()
        for i in range(5):
            tot += 1
            if (int(ft[2 * i], 16), int(ft[2 * i + 1], 16)) != \
               (int(jt[2 * i], 16), int(jt[2 * i + 1], 16)):
                mm += 1
                if len(first) < 5:
                    first.append((inp.strip(), i, a.strip(), c.strip()))
    return mm, tot, first


def seeded(rng, w, n):
    t = 10 if w == 16 else 23 if w == 32 else 52
    emaxf = (1 << (w - 1 - t)) - 1
    n_out = 0
    while n_out < n:
        a, b = rng.getrandbits(w), rng.getrandbits(w)
        if ((a >> t) & emaxf) == emaxf or ((b >> t) & emaxf) == emaxf:
            continue
        yield a, b
        n_out += 1


def main():
    print("JAM-vs-FLOOR f16 pool sweep:", flush=True)
    mm, tot, first = run_both(0, ((p, b) for p in POOL
                                       for b in range(65536)))
    print(f"JAM-F16-POOL: pairs={tot // 5} decisions={tot} "
          f"divergences={mm}", flush=True)
    for inp, i, a, c in first:
        print(f"  {inp} rm={i} floor='{a}' jam='{c}'")
    for fi, w, n in ((1, 32, 200000), (2, 64, 200000)):
        rng = random.Random(0xa + fi)
        print(f"JAM-vs-FLOOR f{w} seeded:", flush=True)
        mm2, tot2, first2 = run_both(fi, seeded(rng, w, n))
        print(f"JAM-F{w}-SEED: pairs={tot2 // 5} decisions={tot2} "
              f"divergences={mm2}", flush=True)
        for inp, i, a, c in first2:
            print(f"  {inp} rm={i} floor='{a}' jam='{c}'")
        mm += mm2
        tot += tot2
    print("JAM-KERNEL", "DIVERGES" if mm else "IDENTICAL",
          f"(total decisions={tot} divergences={mm})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
