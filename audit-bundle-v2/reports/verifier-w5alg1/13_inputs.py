"""13_inputs.py - verifier's OWN directed+seeded input families (f32/f64).

Directed: binade edges (1..6 neighbors, one, minnorm, maxsubnorm,
maxfin), powers of two across the exponent range with +-1 ulp
neighbors (covers odd/even E' shapes), smallest-subnormal class,
perfect-square lattice with neighbors (exact-result cases),
odd-factor scaled squares. Seeded: fixed-seed PRNG finite
encodings (both signs + zeros; inf/NaN excluded - specials are
covered separately). Writes hex lists, prints counts.
"""
import random
import sys

FMTS = {
    "f32": {"bits": 32, "w": 8, "bias": 127},
    "f64": {"bits": 64, "w": 11, "bias": 1023},
}
SEED_N = 20000


def params(fmt):
    d = FMTS[fmt]
    t = {"f32": 23, "f64": 52}[fmt]
    return {"bits": d["bits"], "w": d["w"], "t": t, "bias": d["bias"],
            "emin": 1 - d["bias"], "emax": d["bias"],
            "emaxf": (1 << d["w"]) - 1}


def enc(fmt, sign, ef, frac):
    q = params(fmt)
    return (sign << (q["bits"] - 1)) | (ef << q["t"]) | frac


def encode_pow2(fmt, e):
    q = params(fmt)
    if not (q["emin"] <= e <= q["emax"]):
        return None
    return enc(fmt, 0, e + q["bias"], 0)


def directed(fmt):
    q = params(fmt)
    t = q["t"]
    out = set()
    mask = (1 << q["bits"]) - 1

    def add_nb(x, n=2):
        for d in range(-n, n + 1):
            y = x + d
            if 0 <= y <= mask:
                out.add(y)

    minnorm = 1 << t
    maxsub = minnorm - 1
    maxfin = enc(fmt, 0, q["emaxf"] - 1, (1 << t) - 1)
    for x in list(range(0, 7)) + [minnorm, maxsub, maxfin,
                                  enc(fmt, 0, q["bias"], 0)]:
        add_nb(x, 2)
    # negative-side edges (specials coverage inside directed set)
    for x in [1 << (q["bits"] - 1), minnorm | (1 << (q["bits"] - 1)),
              maxfin | (1 << (q["bits"] - 1))]:
        add_nb(x, 1)
    for e in [q["emin"], q["emin"] + 1, -64, -32, -16, -8, -4, -2, -1,
              0, 1, 2, 4, 8, 16, 32, 64, q["emax"] - 1, q["emax"]]:
        x = encode_pow2(fmt, e)
        if x is not None:
            add_nb(x, 1)
    for f_ in (1, 2, 3, 5, 7, 11, 101):
        if f_ < (1 << t):
            out.add(f_)
    # perfect squares -> exact results, with neighbors
    for k in (1, 2, 3, 5, 7, 16, 25, 49):
        for j in (-3, -1, 0, 1):
            v = k * k * (2.0 ** (2 * j))
            import math
            m, e = math.frexp(v)
            if e - 1 > q["emax"] or e - 1 < q["emin"] - t:
                continue
            sig = int(math.ldexp(m, t + 1))
            if sig >= (1 << (t + 1)):
                sig >>= 1
                e += 1
            ee = e - 1
            if ee >= q["emin"]:
                x = enc(fmt, 0, ee + q["bias"], sig - (1 << t))
            else:
                s = sig >> (q["emin"] - ee)
                if s == 0 or s >= (1 << t):
                    continue
                x = s
            add_nb(x, 1)
    for k in (3, 5, 11, 101, 1001):
        for e in (-13, 0, 17):
            v = k * k * (2.0 ** e)
            import math
            if not math.isfinite(v):
                continue
            m, ee = math.frexp(v)
            ue = ee - 1
            sig = int(math.ldexp(m, t + 1))
            if sig >= (1 << (t + 1)):
                sig >>= 1
                ue += 1
            if ue >= q["emin"] and sig < (1 << (t + 1)):
                x = enc(fmt, 0, ue + q["bias"], sig - (1 << t))
                out.add(x)
    return sorted(out)


def seeded(fmt, n, seed):
    q = params(fmt)
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        x = rng.getrandbits(q["bits"])
        ef = (x >> q["t"]) & q["emaxf"]
        if ef == q["emaxf"]:
            continue
        out.append(x)
    return out


def main():
    which = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else SEED_N
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 20261028
    xs = directed(which)
    print("directed %s: %d inputs" % (which, len(xs)))
    sd = seeded(which, n, seed + (1 if which == "f32" else 2))
    print("seeded %s: %d inputs" % (which, len(sd)))
    with open("scratch/verifier-w5alg1/out/inputs_%s.txt" % which, "w") as fh:
        for x in xs + sd:
            fh.write("%x\n" % x)
    print("wrote inputs_%s.txt: %d total" % (which, len(xs) + len(sd)))


if __name__ == "__main__":
    main()
