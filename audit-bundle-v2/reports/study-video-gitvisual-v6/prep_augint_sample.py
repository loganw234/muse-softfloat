"""Prep for the v6 augmented-interval gate window: pick ONE real row
from muse-softfloat/tests/interval_catalogue.tsv and compute, in exact
arithmetic, what the three stages see for the ray-sphere discriminant
disc = b*b - a*c, a=D.D, b=L.D, c=L.L-r*r, L=O-C (the formula in
board/interval_workload.c iw_sphere_stage{1,2,3} and the oracle in
tests/gen_interval_catalogue.py disc_exact).

Stage 3 (exact): Fraction arithmetic on the exact values of the stored
binary64 bit patterns - identical method to the catalogue oracle; the
result is cross-checked against the row's exact / exact_extra columns
and the script FAILS if they disagree. This value is real, not a
drawing.

Stages 1/2 (binary32 / binary64 intervals): a directed-rounding
replay - every op evaluated exactly (Fraction) then rounded outward
onto the binary32 / binary64 grid (lo down, hi up), inputs enclosed
outward the same way. Same op sequence as the C (dot products summed
x,y,z; disc = b^2 - a*c), but it is a Python replay, so on screen it
is labelled illustration; only the stage-3 sign is claimed real.

Selection rule (deterministic): first sphere row, scanning in file
order, where BOTH the stage-1 and stage-2 intervals straddle zero
(so both cheap stages answer UNCERTAIN) and the exact sign is HIT or
MISS. Prints every input. Writes augint_sample.json next to itself.

Run: $MSF_PYTHON prep_augint_sample.py
"""
from __future__ import annotations

import json, math, struct, sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
TSV = HERE.parent.parent / "muse-softfloat" / "tests" / "interval_catalogue.tsv"


def f_of_bits(b):
    return struct.unpack(">d", struct.pack(">Q", int(b, 16)))[0]


def grid_round(fr: Fraction, prec_bits: int, direction: str) -> Fraction:
    """Round exact Fraction onto the binary grid with prec_bits-bit
    significand (24 for binary32, 53 for binary64), down or up.
    Normal range only - catalogue geometry is O(1)..O(2^16)."""
    if fr == 0:
        return Fraction(0)
    neg = fr < 0
    a = -fr if neg else fr
    e = a.numerator.bit_length() - a.denominator.bit_length()
    while Fraction(2) ** e > a:
        e -= 1
    while Fraction(2) ** (e + 1) <= a:
        e += 1
    ulp = Fraction(2) ** (e - (prec_bits - 1))
    q = a / ulp
    lo = Fraction(math.floor(q)) * ulp
    hi = lo if q == math.floor(q) else lo + ulp
    down, up = (-hi, -lo) if neg else (lo, hi)
    return down if direction == "down" else up


class Iv:
    """Interval over Fractions, every op rounded outward to the grid."""
    def __init__(self, lo, hi, prec):
        self.lo, self.hi, self.p = lo, hi, prec

    @staticmethod
    def point(fr, prec):
        return Iv(grid_round(fr, prec, "down"), grid_round(fr, prec, "up"), prec)

    def _o(self, lo, hi):
        return Iv(grid_round(lo, self.p, "down"), grid_round(hi, self.p, "up"), self.p)

    def sub(self, o):
        return self._o(self.lo - o.hi, self.hi - o.lo)

    def add(self, o):
        return self._o(self.lo + o.lo, self.hi + o.hi)

    def mul(self, o):
        ps = [self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi]
        return self._o(min(ps), max(ps))

    def sqr(self):
        if self.lo >= 0:
            return self._o(self.lo * self.lo, self.hi * self.hi)
        if self.hi <= 0:
            return self._o(self.hi * self.hi, self.lo * self.lo)
        return self._o(Fraction(0), max(self.lo * self.lo, self.hi * self.hi))


def disc_interval(O, D, C, r, prec):
    L = [Iv.point(O[i], prec).sub(Iv.point(C[i], prec)) for i in range(3)]
    Dv = [Iv.point(D[i], prec) for i in range(3)]
    a = Dv[0].sqr().add(Dv[1].sqr()).add(Dv[2].sqr())
    b = L[0].mul(Dv[0]).add(L[1].mul(Dv[1])).add(L[2].mul(Dv[2]))
    c = L[0].sqr().add(L[1].sqr()).add(L[2].sqr()).sub(Iv.point(r, prec).sqr())
    return b.sqr().sub(a.mul(c))


def disc_exact(O, D, C, r):
    L = [O[i] - C[i] for i in range(3)]
    a = sum(D[i] * D[i] for i in range(3))
    b = sum(L[i] * D[i] for i in range(3))
    c = sum(L[i] * L[i] for i in range(3)) - r * r
    return b * b - a * c


def fmt(fr: Fraction, sig=4):
    """Short decimal for screen use, e.g. -1.54e-4 / 0.3869."""
    if fr == 0:
        return "0"
    x = float(fr)
    if 1e-3 <= abs(x) < 1e4:
        return f"{x:.{sig}g}"
    e = math.floor(math.log10(abs(x)))
    m = x / 10 ** e
    return f"{m:.2f}e{e:+d}".replace("e+", "e").replace("e0", "e")


def main():
    rows = []
    for line in TSV.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        f = line.split("\t")
        if f[2] == "sphere":
            rows.append(f)
    print(f"catalogue: {TSV} ({len(rows)} sphere rows scanned in file order)")
    chosen = None
    for f in rows:
        O = [Fraction(f_of_bits(x)) for x in f[4:7]]
        D = [Fraction(f_of_bits(x)) for x in f[7:10]]
        C = [Fraction(f_of_bits(x)) for x in f[10:13]]
        r = Fraction(f_of_bits(f[13]))
        exact = disc_exact(O, D, C, r)
        cls = "HIT" if exact >= 0 else "MISS"
        assert cls == f[16], f"row {f[0]}: class {cls} != TSV {f[16]}"
        assert f"{exact.numerator}/{exact.denominator}" == f[18], \
            f"row {f[0]}: exact disc disagrees with TSV exact_extra"
        i1 = disc_interval(O, D, C, r, 24)
        i2 = disc_interval(O, D, C, r, 53)
        for iv, nm in ((i1, "stage1"), (i2, "stage2")):
            assert iv.lo <= exact <= iv.hi, f"row {f[0]}: {nm} does not enclose exact"
        if i1.lo < 0 < i1.hi and i2.lo < 0 < i2.hi:
            chosen = (f, O, D, C, r, exact, i1, i2)
            break
    assert chosen, "no row with both cheap stages straddling zero"
    f, O, D, C, r, exact, i1, i2 = chosen
    out = {
        "row_id": int(f[0]), "family": f[1], "kind": f[2], "provenance": f[3],
        "O_bits": f[4:7], "D_bits": f[7:10], "C_bits": f[10:13], "r_bits": f[13],
        "O": [float(x) for x in O], "D": [float(x) for x in D],
        "C": [float(x) for x in C], "r": float(r),
        "exact_disc_frac": f"{exact.numerator}/{exact.denominator}",
        "exact_disc_float": float(exact),
        "exact_disc_screen": fmt(exact),
        "exact_class": f[16], "naive_class": f[17],
        "stage1_f32": {"lo": float(i1.lo), "hi": float(i1.hi),
                       "lo_screen": fmt(i1.lo), "hi_screen": fmt(i1.hi),
                       "width": float(i1.hi - i1.lo)},
        "stage2_f64": {"lo": float(i2.lo), "hi": float(i2.hi),
                       "lo_screen": fmt(i2.lo), "hi_screen": fmt(i2.hi),
                       "width": float(i2.hi - i2.lo)},
    }
    (HERE / "augint_sample.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"CHOSEN row id={f[0]} family={f[1]} kind=sphere provenance={f[3]!r}")
    print(f"  O={[float(x) for x in O]} D={[float(x) for x in D]}")
    print(f"  C={[float(x) for x in C]} r={float(r)}")
    print(f"  stage1 binary32 interval: [{fmt(i1.lo)}, {fmt(i1.hi)}]  (straddles 0 -> UNCERTAIN)")
    print(f"  stage2 binary64 interval: [{fmt(i2.lo)}, {fmt(i2.hi)}]  (straddles 0 -> UNCERTAIN)")
    print(f"  stage3 exact disc = {exact.numerator}/{exact.denominator} = {fmt(exact)}"
          f"  -> {'HIT' if exact >= 0 else 'MISS'} (TSV exact={f[16]}, naive={f[17]})")
    print(f"  width ratio stage1/stage2 = {float((i1.hi-i1.lo)/(i2.hi-i2.lo)):.3g}")
    print("wrote augint_sample.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
