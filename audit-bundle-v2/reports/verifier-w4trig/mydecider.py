"""Independent sinPi/cosPi decider (mpmath route, own code).

Decodes bit patterns to exact Fractions, applies the settled specials
(NaN/inf/zero/integer/half-integer, own restatement), else reduces
exactly (nearest-integer + fold to t in [0,1/4]) and evaluates with
mpmath at two precisions (stability recheck). Rounds the exact
high-precision Fraction in all four modes with a first-principles
rounder; flags computed from first principles (inexact always on the
kernel path; underflow = tiny-after-rounding & inexact). Refuses
(undecided) unless both precisions agree and the value clears every
rounding boundary by > 2^-80 relative.

Usage: python3 mydecider.py INFILE OUTFILE
  INFILE lines: "msf16_sin_pi 3c00" (op bits-hex). OUTFILE lines:
  "op bits rb_te rf_te rb_tz rf_tz rb_tp rf_tp rb_tn rf_tn" or UNDECIDED.
"""
import math
import sys
from fractions import Fraction

import mpmath

DPS_PAIRS = ((130, 170, 80), (350, 400, 200), (800, 900, 500))
CLEAR_BITS = 80  # set per attempt from DPS_PAIRS

FMTS = {"msf16": (16, 5), "msf32": (32, 8), "msf64": (64, 11)}
RMS = ("te", "tz", "tp", "tn")


def params(fmt):
    bits, w = FMTS[fmt]
    t = bits - 1 - w
    return {"bits": bits, "w": w, "t": t, "p": t + 1,
            "bias": (1 << (w - 1)) - 1, "emaxf": (1 << w) - 1,
            "sign": 1 << (bits - 1), "fracmask": (1 << t) - 1,
            "qbit": 1 << (t - 1), "inf": ((1 << w) - 1) << t,
            "one": (((1 << (w - 1)) - 1) << t)}


def decode(fmt, x):
    q = params(fmt)
    sign = (x >> (q["bits"] - 1)) & 1
    e = (x >> q["t"]) & q["emaxf"]
    frac = x & q["fracmask"]
    if e == q["emaxf"]:
        return sign, None, None, ("qnan" if frac & q["qbit"] else "snan") \
            if frac else "inf"
    if e == 0:
        if frac == 0:
            return sign, None, None, "zero"
        return sign, Fraction(frac), (1 - q["bias"]) - q["t"], "finite"
    sig = frac | (1 << q["t"])
    return sign, Fraction(sig), e - q["bias"] - q["t"], "finite"


def specials(fmt, fn, x):
    """Settled-table expectations ((bits, flags) x4) or None."""
    q = params(fmt)
    is_cos = fn == "cos_pi"
    sign, sig, exp2, cls = decode(fmt, x)
    sbit = sign << (q["bits"] - 1)
    if cls in ("qnan", "snan"):
        r = x | q["qbit"]
        fl = 0 if (cls == "qnan") else 0x01
        return [((r, fl))] * 4
    if cls == "inf":
        return [((q["inf"] | q["qbit"], 0x01))] * 4
    if cls == "zero":
        r = q["one"] if is_cos else sbit
        return [((r, 0))] * 4
    v = sig * Fraction(2) ** exp2
    av = abs(v)
    fl = av.numerator // av.denominator
    rem = av - fl
    if rem == 0:
        r = (q["one"] | ((fl & 1) << (q["bits"] - 1))) if is_cos else sbit
        return [((r, 0))] * 4
    if rem == Fraction(1, 2):
        if is_cos:
            return [((0, 0))] * 4  # settled cell B: +0 all modes
        r = q["one"] | ((sign ^ (fl & 1)) << (q["bits"] - 1))
        return [((r, 0))] * 4
    return None


def fmt_vals_around(q, av):
    """Two adjacent nonnegative format values bracketing av (exact)."""
    emin = 1 - q["bias"]
    if av == 0:
        return Fraction(0), Fraction(0), True
    e = av.numerator.bit_length() - av.denominator.bit_length()
    if av < Fraction(2) ** e:
        e -= 1
    while Fraction(2) ** (e + 1) <= av:
        e += 1
    if e >= emin:
        step = Fraction(2) ** (e - q["t"])
    else:
        step = Fraction(2) ** (emin - q["t"])
    k = av // step
    lo = k * step
    hi = lo + step
    return lo, hi, (av == lo)


def round_mag(q, av, rm):
    """Round nonnegative exact av under mode rm -> (mag_bits, exact)."""
    lo, hi, is_exact = fmt_vals_around(q, av)
    emin = 1 - q["bias"]
    emax = q["bias"]
    huge = Fraction(2) ** (emax + 1)  # overflow threshold (first inf-round)
    # candidate magnitudes as Fractions (inf handled by bit pattern)
    if is_exact:
        return av, True
    if rm == "te":
        dlo = av - lo
        dhi = hi - av
        if dlo < dhi:
            return lo, False
        if dhi < dlo:
            return hi, False
        # tie: even (least mantissa bit even); hi of subnormal edge...
        return (lo if mag_is_even(q, lo) else hi), False
    if rm == "tz":
        return lo, False
    if rm == "tp":
        return hi, False
    if rm == "tn":
        return lo, False
    raise AssertionError


def mag_is_even(q, mag):
    if mag == 0:
        return True
    emin = 1 - q["bias"]
    e = mag.numerator.bit_length() - mag.denominator.bit_length()
    if mag < Fraction(2) ** e:
        e -= 1
    if e >= emin:
        step = Fraction(2) ** (e - q["t"])
        k = mag // step
        return (k & 1) == 0
    step = Fraction(2) ** (emin - q["t"])
    k = mag // step
    return (k & 1) == 0


def mag_to_bits(q, sign, mag):
    emin = 1 - q["bias"]
    emax = q["bias"]
    if mag >= Fraction(2) ** (emax + 1):
        return (sign << (q["bits"] - 1)) | q["inf"]
    if mag == 0:
        return sign << (q["bits"] - 1)
    e = mag.numerator.bit_length() - mag.denominator.bit_length()
    if mag < Fraction(2) ** e:
        e -= 1
    while Fraction(2) ** (e + 1) <= mag:
        e += 1
    if e >= emin:
        step = Fraction(2) ** (e - q["t"])
        k = mag // step
        assert mag == k * step
        frac = (k - (1 << q["t"])) & q["fracmask"]
        return ((sign << (q["bits"] - 1)) | ((e + q["bias"]) << q["t"])
                | frac)
    step = Fraction(2) ** (emin - q["t"])
    k = mag // step
    assert mag == k * step
    return (sign << (q["bits"] - 1)) | (k & q["fracmask"])


def decide_kernel(fmt, fn, x):
    """Decide a non-special input; raises _Undecided when unclear."""
    q = params(fmt)
    is_cos = fn == "cos_pi"
    sign, sig, exp2, cls = decode(fmt, x)
    assert cls == "finite"
    v = sig * Fraction(2) ** exp2
    av = abs(v)
    # exact reduction: nearest integer + fold to [0,1/4]
    fl = av.numerator // av.denominator
    rem = av - fl
    if rem > Fraction(1, 2):
        n = fl + 1
        r = rem - 1  # negative: r in [-1/2, 0)
    elif rem == Fraction(1, 2):
        raise AssertionError("special leaked")
    else:
        n = fl
        r = rem
    parity = int(n & 1)
    ar = abs(r)
    t = ar if ar <= Fraction(1, 4) else Fraction(1, 2) - ar
    swapped = ar > Fraction(1, 4)
    r_neg = r < 0
    shape_sin = (not swapped) if not is_cos else swapped
    # sinPi(x) = sgn(x)*(-1)^n*sin(pi r); cosPi = (-1)^n*cos(pi r).
    # sin(pi r) = sign(r)*M with M the folded positive kernel value
    # (sin- or cos-shaped, both positive), so any negative remainder
    # flips the delivered sin sign; cos is even, unaffected.
    out_sign = (sign ^ parity ^ (1 if r_neg else 0)) \
        if not is_cos else parity
    assert t > 0
    last_err = None
    for DPS_LO, DPS_HI, CLEAR in DPS_PAIRS:
        try:
            return decide_kernel_at(q, shape_sin, out_sign, t, DPS_LO,
                                    DPS_HI, CLEAR)
        except _Undecided as e:
            last_err = e
    raise last_err


def decide_kernel_at(q, shape_sin, out_sign, t, DPS_LO, DPS_HI,
                     CLEAR_BITS):
    res = []
    for dps in (DPS_LO, DPS_HI):
        mpmath.mp.dps = dps
        tf = mpmath.mpf(t.numerator) / mpmath.mpf(t.denominator)
        if shape_sin:
            y = mpmath.sin(mpmath.pi * tf)
        else:
            y = mpmath.cos(mpmath.pi * tf)
        _s, man, exp, _bc = y._mpf_
        yf = Fraction(man) * Fraction(2) ** exp
        if _s:
            yf = -yf
        assert yf > 0
        res.append(yf)
    ylo, yhi = res
    # magnitude-mode mirror: tp/tn swap for negative results because
    # round_mag works on the nonnegative magnitude.
    magmode = [rm if not out_sign else
               {"te": "te", "tz": "tz", "tp": "tn", "tn": "tp"}[rm]
               for rm in RMS]
    outs = [round_mag(q, ylo, mm) for mm in magmode]
    outs2 = [round_mag(q, yhi, mm) for mm in magmode]
    if outs != outs2:
        raise _Undecided("precision instability")
    # strict-interiority clearance at both precisions: the true value
    # (within ~2^-400 relative of either approximation) must lie in
    # the same open interval between adjacent magnitudes, strictly
    # off the te midpoint too.
    for yv in (ylo, yhi):
        lo, hi, is_exact = fmt_vals_around(q, yv)
        if is_exact:
            raise _Undecided("exact hit (Niven-impossible)")
        if min(yv - lo, hi - yv) * 2 ** CLEAR_BITS < yv:
            raise _Undecided("too close to representable")
        mid = (lo + hi) / 2
        if yv == mid:
            raise _Undecided("tie hit")
        if abs(yv - mid) * 2 ** CLEAR_BITS < yv:
            raise _Undecided("too close to midpoint")
    # flags: inexact always (Niven irrationality: no dyadic input
    # outside the specials is exactly representable or a midpoint).
    # Underflow per mode: delivered magnitude tiny (after rounding)
    # and inexact. Sound by the interiority clearance above: the true
    # value rounds identically in every mode.
    emin = 1 - q["bias"]
    decided = []
    for rm, (mag, _ex) in zip(RMS, outs):
        bits = mag_to_bits(q, out_sign, mag)
        tiny = mag < Fraction(2) ** emin
        fl = 0x10 | (0x08 if tiny else 0)
        decided.append((bits, fl))
    return decided


class _Undecided(Exception):
    pass


def main():
    inp, outp = sys.argv[1], sys.argv[2]
    n_ok = n_un = 0
    with open(inp) as fh, open(outp, "w") as gh:
        for line in fh:
            t = line.split()
            if len(t) != 2:
                continue
            op, hx = t
            fmt, fn = op.split("_", 1)[0], "_".join(op.split("_")[1:])
            fmt = {"msf16": "msf16", "msf32": "msf32",
                   "msf64": "msf64"}[fmt]
            x = int(hx, 16) & ((1 << params(fmt)["bits"]) - 1)
            try:
                sp = specials(fmt, fn, x)
                if sp is None:
                    sp = decide_kernel(fmt, fn, x)
                gh.write(op + " " + hx)
                for b, f in sp:
                    gh.write(f" {b:x} {f:02x}")
                gh.write("\n")
                n_ok += 1
            except _Undecided as e:
                gh.write(f"UNDECIDED {op} {hx} {e}\n")
                n_un += 1
    print(f"decided={n_ok} undecided={n_un}")
    return 0


sys.exit(main())
