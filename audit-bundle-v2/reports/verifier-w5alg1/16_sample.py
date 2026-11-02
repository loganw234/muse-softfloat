"""16_sample.py - MPFR cross-decide sample vs my decider (finite positive).

Sample: verifier directed positive-finite inputs + 2000 seeded
positive-finite encodings per format. Compares MPFR (te/tz/tp/tn)
against my decider modes 0..3. ta is out of MPFR scope (RNDNA
prohibited); ta validity comes from the no-tie census instead.
"""
import importlib.util
import subprocess

_spec = importlib.util.spec_from_file_location(
    "mydec", "scratch/verifier-w5alg1/10_mydecider.py")
mydec = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mydec)

import random


def positive_directed(fmt):
    q = mydec.fmt_params(fmt)
    nbits = mydec.fmt_bits(fmt)
    t = q["t"]
    out = set()
    mask = (1 << nbits) - 1

    def add_nb(x, n=2):
        for d in range(-n, n + 1):
            y = x + d
            if 0 <= y <= mask:
                out.add(y)

    minnorm = 1 << t
    maxsub = minnorm - 1
    maxfin = ((q["emaxf"] - 1) << t) | ((1 << t) - 1)
    for x in list(range(1, 7)) + [minnorm, maxsub, maxfin,
                                  q["bias"] << t]:
        add_nb(x, 2)
    for e in [q["emin"], q["emin"] + 1, -32, -8, -2, -1, 0, 1, 2, 8,
              32, 64, q["emax"] - 1, q["emax"]]:
        if q["emin"] <= e <= q["emax"]:
            add_nb(((e + q["bias"]) << t), 1)
    for f_ in (1, 2, 3, 5, 7, 11, 101):
        if f_ < (1 << t):
            out.add(f_)
    for k in (1, 2, 3, 5, 7, 16, 25, 49):
        for j in (-3, -1, 0, 1):
            v = k * k * (2.0 ** (2 * j))
            import math
            if not math.isfinite(v) or v <= 0:
                continue
            m, ee = math.frexp(v)
            ue = ee - 1
            sig = int(math.ldexp(m, t + 1))
            if sig >= (1 << (t + 1)):
                sig >>= 1
                ue += 1
            if ue >= q["emin"] and sig < (1 << (t + 1)):
                add_nb(((ue + q["bias"]) << t) | (sig - (1 << t)), 1)
    rng = random.Random(777000 + nbits)
    n = 0
    while n < 2000:
        x = rng.getrandbits(nbits) & ((1 << (nbits - 1)) - 1)
        ef = (x >> t) & q["emaxf"]
        if ef == q["emaxf"] or x == 0:
            continue
        out.add(x)
        n += 1
    # MPFR path is finite-positive only: drop zeros / inf-class
    # neighbors the directed expansion may have pulled in.
    out = {x for x in out if x != 0 and ((x >> t) & q["emaxf"]) != q["emaxf"]}
    return sorted(out)


for fmt in ("f16", "f32", "f64"):
    xs = positive_directed(fmt)
    with open("scratch/verifier-w5alg1/out/mpx_%s.txt" % fmt, "w") as fh:
        for x in xs:
            fh.write("%s %x\n" % (fmt, x))
    print("sample %s: %d positive-finite inputs" % (fmt, len(xs)))

proc = subprocess.run(
    ["scratch/verifier-w5alg1/out/mpfrx.exe"],
    stdin=open("scratch/verifier-w5alg1/out/mpx_f16.txt"),
    capture_output=True, text=True)
lines16 = proc.stdout.splitlines()
proc = subprocess.run(
    ["scratch/verifier-w5alg1/out/mpfrx.exe"],
    stdin=open("scratch/verifier-w5alg1/out/mpx_f32.txt"),
    capture_output=True, text=True)
lines32 = proc.stdout.splitlines()
proc = subprocess.run(
    ["scratch/verifier-w5alg1/out/mpfrx.exe"],
    stdin=open("scratch/verifier-w5alg1/out/mpx_f64.txt"),
    capture_output=True, text=True)
lines64 = proc.stdout.splitlines()

total = mism = 0
for line in lines16 + lines32 + lines64:
    tk = line.split()
    if len(tk) != 11 or tk[0] != "M":
        print("MALFORMED MPFR LINE:", line[:100])
        continue
    fmt, inhx = tk[1], tk[2]
    mpfr = [(int(tk[3 + 2 * i], 16), int(tk[4 + 2 * i], 16))
            for i in range(4)]
    mine = mydec.decide(fmt, int(inhx, 16))[:4]
    for i in range(4):
        total += 1
        if mpfr[i] != mine[i]:
            mism += 1
            if mism <= 10:
                print("XDECIDE-MISMATCH %s %s mode=%d mpfr=%x/%02x mine=%x/%02x"
                      % (fmt, inhx, i, mpfr[i][0], mpfr[i][1],
                         mine[i][0], mine[i][1]))
print("MPFR cross-decide vs own decider (te/tz/tp/tn, finite positive): "
      "total=%d mismatches=%d" % (total, mism))
