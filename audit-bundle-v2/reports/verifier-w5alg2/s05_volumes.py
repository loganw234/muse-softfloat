#!/usr/bin/env python3
"""s05_volumes.py - sampled + directed volumes, kernel floor vs fastdec.

f16: 300k seeded pairs (finite + specials-bearing, unfiltered).
f32/f64: independent directed family (boundary pool squared both
orders, exponent lattice both orders, subnormal corners, Pythagorean
exacts with signs) + 200k seeded finite pairs each.
Counts printed per family; mismatch pairs saved.
"""
import random
import subprocess
import sys
import os

sys.path.insert(0, "scratch/verifier-w5alg2")
from mydecide import FMTS  # noqa: E402

OUT = "scratch/verifier-w5alg2/out"
EXE = OUT + "/harness_floor.exe"
FASTDEC = "scratch/verifier-w5alg2/fastdec.py"
PY = os.environ.get("MSF_PYTHON", "python")
RMS = ("te", "tz", "tp", "tn", "ta")


def run_both(fi, pairs):
    blob = "".join(f"{fi} {a:x} {b:x}\n" for a, b in pairs)
    kh = subprocess.run([EXE, "hypot"], input=blob, capture_output=True,
                        text=True)
    if kh.returncode != 0:
        raise RuntimeError(kh.stderr[-2000:])
    fd = subprocess.run([PY, FASTDEC], input=blob, capture_output=True,
                        text=True)
    if fd.returncode != 0:
        raise RuntimeError(fd.stderr[-2000:])
    kl, fl = kh.stdout.splitlines(), fd.stdout.splitlines()
    assert len(kl) == len(fl) == len(pairs)
    return kl, fl


def check(tag, fi, pairs, mf):
    kl, fl = run_both(fi, pairs)
    total = mm = 0
    mm_mode = [0] * 5
    first = []
    for (a, b), kline, fline in zip(pairs, kl, fl):
        kt, ft = kline.split(), fline.split()
        for i in range(5):
            lb, lf = int(kt[2 * i], 16), int(kt[2 * i + 1], 16)
            rb, rf = int(ft[2 * i], 16), int(ft[2 * i + 1], 16)
            total += 1
            if lb != rb or lf != rf:
                mm += 1
                mm_mode[i] += 1
                if len(first) < 4:
                    first.append((a, b, i, lb, lf, rb, rf))
                mf.write(f"{fi} {a:x} {b:x} rm={RMS[i]} "
                         f"kernel={lb:x}/{lf:02x} mine={rb:x}/{rf:02x}\n")
    print(f"{tag}: pairs={len(pairs)} decisions={total} mismatches={mm} "
          f"[te={mm_mode[0]} tz={mm_mode[1]} tp={mm_mode[2]} "
          f"tn={mm_mode[3]} ta={mm_mode[4]}] "
          f"{'PASS' if mm == 0 else 'FAIL'}", flush=True)
    for a, b, i, lb, lf, rb, rf in first:
        print(f"  a={a:x} b={b:x} rm={RMS[i]} "
              f"kernel={lb:x}/{lf:02x} mine={rb:x}/{rf:02x}", flush=True)
    return mm


def seeded(rng, w, n, allow_specials):
    t = 10 if w == 16 else 23 if w == 32 else 52
    emaxf = (1 << (w - 1 - t)) - 1
    out = []
    while len(out) < n:
        a, b = rng.getrandbits(w), rng.getrandbits(w)
        if not allow_specials:
            if ((a >> t) & emaxf) == emaxf or ((b >> t) & emaxf) == emaxf:
                continue
        out.append((a, b))
    return out


def directed(fi):
    f = FMTS[fi]
    t, w = f["t"], f["w"]
    s = 1 << (w - 1)
    inf = (((1 << (w - 1 - t)) - 1) << t)
    minnorm = 1 << t
    one = (f["bias"] << t)
    pool = [0, s, 1, s | 1, 2, (1 << t) - 1, minnorm, minnorm + 1,
            one, one + 1, ((f["bias"] + 1) << t), f["maxfin"], f["maxfin"] - 1,
            inf, inf | s]
    out = [(a, b) for a in pool for b in pool]
    for a, b in list(out[:16]):
        out += [(a | s, b), (a, b | s)]
    exps = sorted({e for e in
                   list(range(f["emin"], f["emin"] + 3)) +
                   [-8, -1, 0, 1, 8] +
                   list(range(f["emax"] - 2, f["emax"] + 1))
                   if f["emin"] <= e <= f["emax"]})
    vals = []
    for e in exps:
        vals.append((((e + f["bias"]) << t)))
    out += [(a, b) for a in vals for b in vals]
    out += [(a, 1) for a in vals] + [(1, a) for a in vals]
    small = [c for c in (1, 2, 3, 5, 16, (1 << t) - 1) if c < (1 << t)]
    out += [(a, b) for a in small for b in small]
    out += [(a, minnorm) for a in small] + [(minnorm, a) for a in small]
    return out


def exact_pairs(fi):
    f = FMTS[fi]
    from fractions import Fraction
    from mydecide import encode_value

    def enc(v):
        return encode_value(fi, v)
    out = []
    for x_, y_ in ((3, 4), (5, 12), (8, 15), (20, 21)):
        for k in (-6, -1, 4):
            try:
                a = enc(Fraction(x_) * Fraction(2) ** k)
                b = enc(Fraction(y_) * Fraction(2) ** k)
            except AssertionError:
                continue
            s = 1 << (f["w"] - 1)
            out += [(a, b), (b, a), (a | s, b), (a, b | s)]
    return out


def main():
    mm = 0
    with open(f"{OUT}/s05_volumes_mism.txt", "w") as mf:
        rng = random.Random(0xf16ee)
        mm += check("SEEDED-F16", 0, seeded(rng, 16, 300000, True), mf)
        rng = random.Random(0x32ee)
        mm += check("DIRECTED-F32", 1, directed(1), mf)
        mm += check("EXACTS-F32", 1, exact_pairs(1), mf)
        mm += check("SEEDED-F32", 1, seeded(rng, 32, 200000, False), mf)
        rng = random.Random(0x64ee)
        mm += check("DIRECTED-F64", 2, directed(2), mf)
        mm += check("EXACTS-F64", 2, exact_pairs(2), mf)
        mm += check("SEEDED-F64", 2, seeded(rng, 64, 200000, False), mf)
    print("VOLUMES", "PASS" if mm == 0 else "FAIL")
    return 0 if mm == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
