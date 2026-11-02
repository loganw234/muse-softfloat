"""18_boundary.py - smallest-normal/subnormal boundary probe.

My decider's decisions on boundary cells, verified by INDEPENDENT
arithmetic (no isqrt, no Q): decode candidate output as an exact
dyadic Fraction and locate the true value y = 1/sqrt(x) by exact
integer compares of m^2 * x vs 1 for the candidate, its +-1 ulp
neighbors, and both adjacent midpoints. Ties (midpoint equality)
are reported, never assumed. Also asserts exactness (yv^2 * x == 1)
exactly where the study's perfect-square criterion says so.
"""
import importlib.util
from fractions import Fraction

_spec = importlib.util.spec_from_file_location(
    "mydec", "scratch/verifier-w5alg1/10_mydecider.py")
mydec = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mydec)
MODES = ("te", "tz", "tp", "tn", "ta")


def decode_frac(fmt, bits):
    q = mydec.fmt_params(fmt)
    c = mydec.classify(fmt, bits)
    kind = c[0]
    if kind == "zero":
        return Fraction(0)
    if kind == "num":
        _, sign, ef, frac = c
        assert sign == 0
        if ef == 0:
            sig, ex = frac, q["emin"] - q["t"]
        else:
            sig, ex = frac | (1 << q["t"]), ef - q["bias"] - q["t"]
        return Fraction(sig) * Fraction(2) ** ex
    raise AssertionError(("non-finite", fmt, hex(bits), kind))


def ulp_of(fmt, bits):
    q = mydec.fmt_params(fmt)
    c = mydec.classify(fmt, bits)
    _, _, ef, _ = c
    return Fraction(2) ** (ef - q["bias"] - q["t"])


def cells(fmt):
    q = mydec.fmt_params(fmt)
    t = q["t"]
    minnorm = 1 << t
    maxsub = minnorm - 1
    maxfin = ((q["emaxf"] - 1) << t) | ((1 << t) - 1)
    xs = [1, 2, 3, maxsub - 1, maxsub, minnorm - 1, minnorm,
          minnorm + 1, maxfin - 1, maxfin,
          q["bias"] << t]  # 1.0
    for e in range(q["emin"], q["emax"] + 1):
        if e % 2 == 0:
            xs.append(((e + q["bias"]) << t))        # 2^e exact
        else:
            xs.append(((e + q["bias"]) << t))        # 2^e odd
            xs.append((((e + q["bias"]) << t) | 1))  # +1ulp neighbor
    return sorted(set(x for x in xs if 0 < x < (1 << mydec.fmt_bits(fmt))
                      and ((x >> t) & q["emaxf"]) != q["emaxf"]))


fails = 0
total = 0
ties = []
for fmt in ("f16", "f32", "f64"):
    for x in cells(fmt):
        xv = decode_frac(fmt, x)
        dec = mydec.decide(fmt, x)
        for mi, mode in enumerate(MODES):
            b, fl = dec[mi]
            yv = decode_frac(fmt, b)
            u = ulp_of(fmt, b)
            total += 1
            yy = yv * yv * xv
            if yy == 1:
                ok = (fl == 0)
                # exact: all modes identical bits
                ok = ok and all(d[0] == b and d[1] == 0 for d in dec)
                if not ok:
                    fails += 1
                    print("BOUNDARY-FAIL exact %s %x mode=%s" % (fmt, x, mode))
                continue
            # inexact: bracket y strictly inside (yv-u, yv+u)
            lo_ok = (yv - u) ** 2 * xv < 1
            hi_ok = (yv + u) ** 2 * xv > 1
            if not (lo_ok and hi_ok):
                fails += 1
                print("BOUNDARY-FAIL bracket %s %x mode=%s" % (fmt, x, mode))
                continue
            if fl != mydec.INEXACT:
                fails += 1
                print("BOUNDARY-FAIL flag %s %x mode=%s" % (fmt, x, mode))
                continue
            # directed checks
            if mode in ("tz", "tn"):
                if not ((yv * yv * xv <= 1)
                        and ((yv + u) ** 2 * xv > 1)):
                    fails += 1
                    print("BOUNDARY-FAIL down %s %x" % (fmt, x))
            elif mode == "tp":
                if not (((yv - u) ** 2 * xv < 1)
                        and (yv * yv * xv >= 1)):
                    fails += 1
                    print("BOUNDARY-FAIL up %s %x" % (fmt, x))
            else:  # te / ta: strictly between midpoints, no tie
                mlo = yv - u / 2
                mhi = yv + u / 2
                slo = mlo * mlo * xv
                shi = mhi * mhi * xv
                if slo == 1 or shi == 1:
                    ties.append((fmt, x, mode))
                    print("BOUNDARY-TIE %s %x mode=%s" % (fmt, x, mode))
                elif not (slo < 1 and shi > 1):
                    fails += 1
                    print("BOUNDARY-FAIL nearest %s %x mode=%s"
                          % (fmt, x, mode))
print("boundary probe: total=%d fails=%d ties=%d" % (total, fails, len(ties)))
