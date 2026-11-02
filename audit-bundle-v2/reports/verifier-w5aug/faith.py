#!/usr/bin/env python3
"""faith.py - verifier-w5aug: adapted-harness reference vs myref.py on
seeded random f16 pairs + directed extremes. Proves the u128->u64
adaptation is faithful before pool/slice verdicts are quoted."""
import random
import subprocess
import sys

sys.path.insert(0, sys.path[0])
from myref import ref

OPS = ("add", "sub", "mul")


def gen(n, seed):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        r = rng.random()
        if r < 0.5:
            a, b = rng.getrandbits(16), rng.getrandbits(16)
        elif r < 0.65:
            # finite-biased: normal bit patterns
            a = rng.getrandbits(16) & 0x7BFF
            b = rng.getrandbits(16) & 0x7BFF
            if rng.random() < 0.5:
                a |= 0x8000
            if rng.random() < 0.5:
                b |= 0x8000
        elif r < 0.8:
            # close exponents
            e = rng.randrange(1, 31)
            a = (e << 10) | rng.getrandbits(10)
            b = ((min(e + rng.randrange(-2, 3), 30)) << 10) | rng.getrandbits(10)
            if e + rng.randrange(-2, 3) <= 0:
                b = rng.getrandbits(10)
        else:
            # tiny-biased
            a = rng.getrandbits(11)
            b = rng.getrandbits(11)
        out.append((rng.choice(OPS), a & 0xFFFF, b & 0xFFFF))
    # directed extremes
    ext = [0x0000, 0x8000, 0x0001, 0x8001, 0x03FF, 0x0400, 0x3C00, 0xBC00,
           0x7BFF, 0xFBFF, 0x7C00, 0xFC00, 0x7E00, 0x7C01, 0x3555, 0x7800]
    for a in ext:
        for b in ext:
            for op in OPS:
                out.append((op, a, b))
    return out


def main():
    refdump = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 300000
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 20261029
    cs = gen(n, seed)
    inp = "".join("%s %04x %04x\n" % c for c in cs)
    p = subprocess.run([refdump], input=inp, capture_output=True, text=True)
    lines = p.stdout.strip().split("\n")
    assert len(lines) == len(cs), (len(lines), len(cs))
    bad = 0
    for (op, a, b), ln in zip(cs, lines):
        t = ln.split()
        assert t[3] == "->", ln
        eh, et, ef = ref("f16", op, a, b)
        if (t[4], t[5], int(t[6], 16)) != ("%04x" % eh, "%04x" % et, ef):
            bad += 1
            if bad <= 10:
                print("FAITH-MISMATCH %s %04x %04x: harness %s %s/%s myref %04x %04x/%02x" % (
                    op, a, b, t[4], t[5], t[6], eh, et, ef))
    print("faith: %d cases, %d mismatches" % (len(cs), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
