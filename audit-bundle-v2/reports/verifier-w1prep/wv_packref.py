#!/usr/bin/env python3
"""wv_packref.py - INDEPENDENT exact-rational reference for msf_pack_generic.

Written from scratch for verifier-w1prep. Does NOT import or reuse
tests/gen_vectors.py. Organization differs deliberately: the exact value
is kept as an integer numerator over a power-of-two denominator
(NUM / 2^DEN), rounding is done by pure integer division against the
target ulp, and overflow/underflow/packing are decided from the rounded
integer. Cross-checked against committed pack16/32/64.vec lines and
against fresh directed cases per width via wv_packdrv (C caller of
msf_pack_generic).

Kernel contract under test (src/msf_internal.h):
  exact magnitude = (sig + f) * 2^exp2, f = 0 if sticky == 0,
  0 < f < 1 if sticky != 0. sig == 0 with sticky != 0 is OUTSIDE the
  domain (callers jam); such inputs are skipped, never asserted.
Flag bits: INVALID=0x01 DIV0=0x02 OVF=0x04 UNF=0x08 INX=0x10.
Tininess: AFTER rounding (SF-0 2.5).
"""
import subprocess
import sys
from fractions import Fraction

FORMATS = {
    "f16": {"bits": 16, "p": 11, "t": 10, "emax": 15, "emin": -14, "bias": 15},
    "f32": {"bits": 32, "p": 24, "t": 23, "emax": 127, "emin": -126, "bias": 127},
    "f64": {"bits": 64, "p": 53, "t": 52, "emax": 1023, "emin": -1022, "bias": 1023},
}
OVF, UNF, INX = 0x04, 0x08, 0x10
RM_NAMES = ["te", "tz", "tp", "tn", "ta"]
FRACS = [Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)]


def ref_pack(fmt, sign, exp2, sig, sticky, rm):
    """Return {(bits, flags)} outcome set over f in {0} or {1/4,1/2,3/4}."""
    fp = FORMATS[fmt]
    p, emax, emin = fp["p"], fp["emax"], fp["emin"]
    t = fp["t"]
    out = set()
    fvals = [Fraction(0)] if not sticky else list(FRACS)
    for f in fvals:
        if sig == 0:
            out.add((sign << (fp["bits"] - 1), 0))  # caller domain: sticky==0 here
            continue
        v = (sig + f) * (Fraction(2) ** exp2)  # exact magnitude, always > 0
        # e = exponent of top bit: 2^e <= v < 2^(e+1)
        e = v.numerator.bit_length() - v.denominator.bit_length()
        if Fraction(2) ** (e + 1) <= v:
            e += 1
        while Fraction(2) ** e > v:
            e -= 1
        # rounding grid: ulp = 2^scale with scale pinned at emin like the kernel
        scale = max(e, emin) - (p - 1)
        units = v / (Fraction(2) ** scale)  # exact, rational
        fl = units.numerator // units.denominator
        rem = units - fl
        inexact = rem != 0
        half = Fraction(1, 2)
        if rm == "te":
            inc = rem > half or (rem == half and (fl & 1) == 1)
        elif rm == "ta":
            inc = rem >= half
        elif rm == "tp":
            inc = (sign == 0) and inexact
        elif rm == "tn":
            inc = (sign == 1) and inexact
        else:  # tz
            inc = False
        q = fl + (1 if inc else 0)
        if q == 2 ** p:
            q >>= 1
            scale += 1
        # overflow?
        maxfinite_num = (2 ** p - 1) * (2 ** (emax - (p - 1)))
        # v_rounded = q * 2^scale
        if q * (Fraction(2) ** scale) > maxfinite_num:
            if rm in ("te", "ta") or (rm == "tp" and sign == 0) or (rm == "tn" and sign == 1):
                enc = ((1 << (fp["bits"] - 1 - t)) - 1) << t  # all-ones exp, frac 0
                out.add(((sign << (fp["bits"] - 1)) | enc, OVF | INX))
            else:
                expall = ((1 << (fp["bits"] - 1 - t)) - 2) << t
                out.add(((sign << (fp["bits"] - 1)) | expall | ((1 << t) - 1), OVF | INX))
            continue
        flags = 0
        if inexact:
            flags |= INX
            if q * (Fraction(2) ** scale) < Fraction(2) ** emin:
                flags |= UNF
        if q >= 2 ** (p - 1):
            enc = ((scale + (p - 1) + fp["bias"]) << t) | (q - 2 ** (p - 1))
            out.add(((sign << (fp["bits"] - 1)) | enc, flags))
        else:
            out.add(((sign << (fp["bits"] - 1)) | q, flags))
    return out


def parse_vec_line(line):
    tok = line.split()
    if len(tok) != 10 or tok[6] != "->":
        return None
    op, rm, sign, exp2, sighex, sticky = tok[0], tok[1], tok[2], tok[3], tok[4], tok[5]
    if not op.startswith("internal.pack"):
        return None
    fmt = "f" + op.rsplit("pack", 1)[1]
    if fmt not in ("f16", "f32", "f64"):
        return None
    return (fmt, rm, int(sign), int(exp2), int(sighex, 16), int(sticky),
            int(tok[7], 16), int(tok[8], 16))


def replay(path):
    """Recompute every committed line with the independent reference."""
    n = mismatch = skipped = 0
    with open(path, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            r = parse_vec_line(line)
            if r is None:
                print("UNPARSEABLE %s:%d: %s" % (path, ln, line))
                mismatch += 1
                continue
            fmt, rm, sign, exp2, sig, sticky, ebits, eflags = r
            if sig == 0 and sticky:
                skipped += 1  # outside kernel domain; generator must not emit these
                continue
            outcomes = ref_pack(fmt, sign, exp2, sig, sticky, rm)
            n += 1
            if len(outcomes) != 1:
                print("NON-INVARIANT committed line %s:%d outcomes=%s" % (path, ln, outcomes))
                mismatch += 1
                continue
            if next(iter(outcomes)) != (ebits & ((1 << FORMATS[fmt]["bits"]) - 1) if FORMATS[fmt]["bits"] < 64 else ebits, eflags):
                got = next(iter(outcomes))
                print("MISMATCH %s:%d ref=(%x,%02x) vec=(%x,%02x) %s" % (
                    path, ln, got[0], got[1], ebits, eflags, line))
                mismatch += 1
    mask_note = "bits masked to width for f16/f32 (vec prints %%016x)"
    return n, mismatch, skipped


def directed_cases(fmt):
    """Own directed design: crossings, overflow/mode/sign, exact subnormals,
    ties both ways, sticky sensitivity. Yields (sign, exp2, sig, sticky, rm)."""
    fp = FORMATS[fmt]
    p, emax, emin = fp["p"], fp["emax"], fp["emin"]
    cases = []
    # (a) smallest-normal crossings: exact 2^emin and neighbors via top-bit sig
    for delta in range(-6, 6):
        for sig in (1 << 127, (1 << 127) + (1 << 60), (1 << 127) - (1 << 60),
                    (1 << 127) | 1, (1 << 126), (1 << 128) - 1):
            exp2 = (emin - 127) + delta
            for sticky in (0, 1):
                for rm in RM_NAMES:
                    for sign in (0, 1):
                        cases.append((sign, exp2, sig, sticky, rm))
    # (b) overflow deliveries per mode/sign: values at/above maxfinite
    for sig in ((1 << 128) - 1, 1 << 127, (1 << 127) + (1 << 100)):
        for exp2 in (emax - 127 - 1, emax - 127, emax - 127 + 1, emax - 100):
            for sticky in (0, 1):
                for rm in RM_NAMES:
                    for sign in (0, 1):
                        cases.append((sign, exp2, sig, sticky, rm))
    # (c) exact subnormals: sig small, exp2 pinned so value is exactly subnormal
    for sig in (1, 2, 3, 7, 1 << 40, (1 << 60) + 1):
        for exp2 in (emin - 120, emin - 60, emin - 10, emin, emin + 5):
            for rm in RM_NAMES:
                for sign in (0, 1):
                    cases.append((sign, exp2, sig, 0, rm))
    # (d) ties both ways at several binades: guard=1 rest=0 exactly halfway
    for e in (emin, emin + 1, -1, 0, 1, emax - 1, emax - 2):
        for rm in RM_NAMES:
            for sign in (0, 1):
                # value (2^p - 1/2-ish): halfway between top two significands
                cases.append((sign, e - 127, ((1 << 128) - (1 << 64)) | (1 << 63), 0, rm))
                cases.append((sign, e - 127, (1 << 127) | (1 << 63), 0, rm))
    # (e) sticky sensitivity pairs: dropped-bits-zero with sticky 0 vs 1
    for sig in (1 << 127, (1 << 127) | (1 << 40), (1 << 120) + 5):
        for exp2 in (emin - 100, -60, 0, emax - 120):
            for rm in RM_NAMES:
                for sign in (0, 1):
                    cases.append((sign, exp2, sig, 0, rm))
                    cases.append((sign, exp2, sig, 1, rm))
    # (f) zero / near-zero domain edges
    for sig in (0, 1):
        for exp2 in (-5000, -1100, 0, 1100, 5000):
            for rm in RM_NAMES:
                for sign in (0, 1):
                    cases.append((sign, exp2, sig, 0, rm))
    # (g) deterministic LCG sweep across the whole input space
    s = 0x12345678 + fp["p"]
    for _ in range(1600):
        s = (1103515245 * s + 12345) & 0xFFFFFFFF
        sig = ((s * 0x9E3779B1) & ((1 << 128) - 1)) ^ (s >> 3)
        if sig == 0:
            sig = 1
        s = (1103515245 * s + 12345) & 0xFFFFFFFF
        span = (emax - 127 + 8) - (emin - 127 - 8) + 1
        exp2 = (emin - 127 - 8) + (s % span)
        s = (1103515245 * s + 12345) & 0xFFFFFFFF
        sticky = (s >> 7) & 1
        rm = RM_NAMES[(s >> 11) % 5]
        sign = (s >> 15) & 1
        cases.append((sign, exp2, sig, sticky, rm))
    # dedupe, drop out-of-domain (sig==0 and sticky)
    seen = set()
    uniq = []
    for c in cases:
        if c[2] == 0 and c[3]:
            continue
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    return uniq


def main():
    if len(sys.argv) < 3:
        print("usage: wv_packref.py DRVEXE OUTFILE")
        return 2
    drvexe, outfile = sys.argv[1], sys.argv[2]
    report = []
    # Part A: replay committed vectors
    total_mm = 0
    for fmt in ("f16", "f32", "f64"):
        path = "muse-softfloat/tests/vectors/pack%s.vec" % fmt[1:]
        n, mm, skipped = replay(path)
        report.append("replay %s: %d lines recomputed, %d mismatches, %d domain-skips" % (path, n, mm, skipped))
        total_mm += mm
    # Part B: directed differential vs C kernel
    grand = {"kept": 0, "dropped": 0, "mismatch": 0}
    first_mm = []
    for fmt in ("f16", "f32", "f64"):
        cases = directed_cases(fmt)
        # keep only sticky-invariant cases (same discipline as the project)
        kept = []
        dropped = 0
        for (sign, exp2, sig, sticky, rm) in cases:
            outcomes = ref_pack(fmt, sign, exp2, sig, sticky, rm)
            if len(outcomes) == 1:
                kept.append((sign, exp2, sig, sticky, rm, next(iter(outcomes))))
            else:
                dropped += 1
        # run C driver
        inp = "".join("%s %s %d %d %032x %d\n" % (fmt, rm, s, e, sg, st)
                      for (s, e, sg, st, rm, _) in kept)
        proc = subprocess.run([drvexe], input=inp, capture_output=True, text=True)
        if proc.returncode != 0:
            print("DRIVER FAILED fmt=%s rc=%d\n%s" % (fmt, proc.returncode, proc.stderr))
            return 1
        lines = proc.stdout.splitlines()
        assert len(lines) == len(kept), (fmt, len(lines), len(kept))
        mm = 0
        for (s, e, sg, st, rm, want), line in zip(kept, lines):
            bits_s, fl_s = line.split()
            got = (int(bits_s, 16), int(fl_s, 16))
            if got != want:
                mm += 1
                if len(first_mm) < 10:
                    first_mm.append("%s %s s=%d e=%d sig=%032x st=%d: C=(%x,%02x) ref=(%x,%02x)" % (
                        fmt, rm, s, e, sg, st, got[0], got[1], want[0], want[1]))
        report.append("directed %s: %d generated, %d kept-invariant, %d dropped, %d C-vs-ref mismatches"
                      % (fmt, len(cases), len(kept), dropped, mm))
        grand["kept"] += len(kept)
        grand["dropped"] += dropped
        grand["mismatch"] += mm
        total_mm += mm
    for m in first_mm:
        report.append("  MM " + m)
    report.append("TOTAL mismatches (replay+differential): %d" % total_mm)
    open(outfile, "w", encoding="utf-8").write("\n".join(report) + "\n")
    print("\n".join(report))
    return 0 if total_mm == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
