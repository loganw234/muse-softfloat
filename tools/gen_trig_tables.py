#!/usr/bin/env python3
"""Generate src/msf_trig_tables.h for the sinPi/cosPi kernel.

First principles only: Taylor coefficients are the exact
rationals 1/(2k+1)! and 1/(2k)!; pi is computed with mpmath
at 260-digit precision and floored to 384-bit limbs by exact
rational arithmetic, with the floor proven stable by checking
that a +-2^-590 bracket around the computed value floors to
the same 384-bit integer (the computation is done at ~865-bit
precision and cross-checked at a second precision; measured
agreement is printed). Every stored entry is the exact floor
of the true constant at 384 bits: stored <= true < stored +
1 ulp, verified per entry with Fractions (for pi, against the
bracket above). The kernel forms coefficient intervals from
these floors; see ledger/parcel-w4trig.md design entry and
scratch/parcel-w4trig/error_budget.py for the budget that
fixes the stage widths, term counts, and tail bounds emitted
here. Regeneration must be byte-identical.

Usage: gen_trig_tables.py OUT.h
"""
import math
import sys
from fractions import Fraction

import mpmath

W_TOP = 384
LIMBS = W_TOP // 32
STAGE_LIMBS = (5, 8, 12)
# pi ceiling for tail bounds (rational, > pi)
PI_HI = Fraction(314159265358979323846264338327950288419716939937511, 10**50)
ZMAX = (PI_HI / 4) ** 2


def floor_entry(v: Fraction):
    """Exact floor of positive Fraction v to a W_TOP-bit
    normalized significand: returns (e, M) with value
    M * 2^(e-(W_TOP-1)) <= v < (M+1) * 2^(e-(W_TOP-1))."""
    assert v > 0
    e = v.numerator.bit_length() - v.denominator.bit_length()
    # adjust: want 2^e <= v < 2^(e+1)
    while Fraction(2) ** e > v:
        e -= 1
    while Fraction(2) ** (e + 1) <= v:
        e += 1
    scaled = v * Fraction(2) ** (W_TOP - 1 - e)
    m = scaled.numerator // scaled.denominator
    assert 2 ** (W_TOP - 1) <= m < 2**W_TOP
    lo = Fraction(m) * Fraction(2) ** (e - (W_TOP - 1))
    hi = Fraction(m + 1) * Fraction(2) ** (e - (W_TOP - 1))
    assert lo <= v < hi
    return e, m


def pi_bracket_floor():
    out = []
    for dps in (260, 210):
        mpmath.mp.dps = dps
        p = mpmath.mp.pi
        sign, man, exp, _bc = p._mpf_
        assert sign == 0
        out.append(Fraction(man) * Fraction(2) ** exp)
    a, b = out
    diff = abs(a - b)
    print(f"# pi: |dps260-dps210| ~= 2^{math.log2(float(diff)):.1f}")
    assert diff < Fraction(2) ** -600
    bracket = Fraction(2) ** -590
    e1, m1 = floor_entry(a - bracket)
    e2, m2 = floor_entry(a + bracket)
    assert (e1, m1) == (e2, m2), "pi floor not bracket-stable"
    return e1, m1


def tail_terms(kind, target_bits):
    k = 0
    while True:
        if kind == "sin":
            term = ZMAX**k / Fraction(math.factorial(2 * k + 1))
            ratio = ZMAX / Fraction((2 * k + 2) * (2 * k + 3))
        else:  # delta D coefficients 2/(2k+2)!
            term = 2 * ZMAX**k / Fraction(math.factorial(2 * k + 2))
            ratio = ZMAX / Fraction((2 * k + 3) * (2 * k + 4))
        if term / (1 - ratio) <= Fraction(1, 2**target_bits):
            return k
        k += 1


def tail_exp(kind, nterms):
    """Smallest T with 2^-T >= alternating tail after nterms."""
    if kind == "sin":
        term = ZMAX**nterms / Fraction(math.factorial(2 * nterms + 1))
        ratio = ZMAX / Fraction((2 * nterms + 2) * (2 * nterms + 3))
    else:
        term = 2 * ZMAX**nterms / Fraction(math.factorial(2 * nterms + 2))
        ratio = ZMAX / Fraction((2 * nterms + 3) * (2 * nterms + 4))
    bound = term / (1 - ratio)
    t = 0
    while Fraction(2) ** -(t + 1) >= bound:
        t += 1
    assert Fraction(2) ** -t >= bound
    return t


S_MIN = Fraction(9003, 10000)
D_MIN = Fraction(9496, 10000)


def scalar_ek_exp(w, n_sin, n_del):
    """Relative-error bound for the scalar truncating
    evaluation (one truncating op or truncated constant errs
    by <= 2^(1-W) relative), as a bit count B with Ek <=
    2^-B. Recurrence re-derived in the parcel ledger design
    entry; must match scratch/parcel-w4trig/error_budget.py,
    checked by the printed values at generation time."""
    eps = Fraction(2, 2**w)
    e_u = 2 * eps + eps * eps
    e_z = 2 * e_u + e_u * e_u + eps

    def tail(kind, nterms):
        if kind == "sin":
            t = ZMAX**nterms / Fraction(math.factorial(2 * nterms + 1))
            r = ZMAX / Fraction((2 * nterms + 2) * (2 * nterms + 3))
        else:
            t = 2 * ZMAX**nterms / Fraction(math.factorial(2 * nterms + 2))
            r = ZMAX / Fraction((2 * nterms + 3) * (2 * nterms + 4))
        return t / (1 - r)

    def horner(kind, nterms, val_min):
        e = eps
        for k in range(nterms - 2, -1, -1):
            if kind == "sin":
                rho = ZMAX / Fraction((2 * k + 2) * (2 * k + 3))
            else:
                rho = ZMAX / Fraction((2 * k + 3) * (2 * k + 4))
            e_prod = e_z + e + e_z * e + eps
            e = (eps + rho * e_prod) / (1 - rho) + eps
        return e + tail(kind, nterms) / val_min

    e_s = horner("sin", n_sin, S_MIN)
    e_sin = e_u + e_s + e_u * e_s + eps
    e_d = horner("delta", n_del, D_MIN)
    e_del = e_z + e_d + e_z * e_d + eps
    bound = max(e_sin, e_del)
    bits = 0
    while Fraction(2) ** -(bits + 1) >= bound:
        bits += 1
    # Ek used in code: 2^-exp with 9 bits of margin under bound
    assert bits > 40
    return bits - 9


def emit_entry(name, e, m):
    limbs = [(m >> (32 * i)) & 0xFFFFFFFF for i in range(LIMBS)]
    body = ", ".join(f"0x{x:08x}u" for x in limbs)
    return f"    {{ {e}, {{ {body} }} }},  /* {name} */"


def main():
    out_path = sys.argv[1]
    stage_nterms = []
    for limbs in STAGE_LIMBS:
        w = 32 * limbs
        ns = tail_terms("sin", w + 24)
        nd = tail_terms("delta", w + 24)
        stage_nterms.append((ns, nd))
    n_sin_max = max(s for s, _ in stage_nterms)
    n_del_max = max(d for _, d in stage_nterms)
    # cos table needs one extra entry: delta d_k = 2 * cos c_{k+1}
    n_cos_max = n_del_max + 1

    pi_e, pi_m = pi_bracket_floor()
    sin_entries = [floor_entry(Fraction(1, math.factorial(2 * k + 1)))
                   for k in range(n_sin_max)]
    cos_entries = [floor_entry(Fraction(1, math.factorial(2 * k)))
                   for k in range(n_cos_max)]

    lines = []
    lines.append("/* msf_trig_tables.h - GENERATED by tools/gen_trig_tables.py;")
    lines.append(" * do not edit. Each entry is the exact 384-bit floor of")
    lines.append(" * the named constant: value in [M, M+1) * 2^(e-383),")
    lines.append(" * M the 12 little-endian limbs. */")
    lines.append("#ifndef MSF_TRIG_TABLES_H")
    lines.append("#define MSF_TRIG_TABLES_H")
    lines.append("")
    lines.append("#include <stdint.h>")
    lines.append("")
    lines.append("#define MSF_TRIG_WTOP 384")
    lines.append("#define MSF_TRIG_MAXL 12")
    lines.append("")
    lines.append("typedef struct msf_trig_entry {")
    lines.append("    int32_t e;")
    lines.append("    uint32_t m[MSF_TRIG_MAXL];")
    lines.append("} msf_trig_entry_t;")
    lines.append("")
    sl = ", ".join(str(x) for x in STAGE_LIMBS)
    lines.append(f"static const int MSF_TRIG_STAGE_LIMBS[3] = {{ {sl} }};")
    ns = ", ".join(str(s) for s, _ in stage_nterms)
    nd = ", ".join(str(d) for _, d in stage_nterms)
    lines.append(f"static const int MSF_TRIG_NTERMS_SIN[3] = {{ {ns} }};")
    lines.append(f"static const int MSF_TRIG_NTERMS_DELTA[3] = {{ {nd} }};")
    ts = ", ".join(str(tail_exp("sin", s)) for s, _ in stage_nterms)
    td = ", ".join(str(tail_exp("delta", d)) for _, d in stage_nterms)
    ek = ", ".join(str(scalar_ek_exp(32 * lb, s, d))
                   for lb, (s, d) in zip(STAGE_LIMBS, stage_nterms))
    lines.append(f"static const int MSF_TRIG_EK_EXP[3] = {{ {ek} }};")
    print(f"# scalar Ek exponents (9-bit margin): {ek}; tails sin={ts} delta={td}")
    lines.append("")
    lines.append(f"#define MSF_TRIG_NSIN {n_sin_max}")
    lines.append(f"#define MSF_TRIG_NCOS {n_cos_max}")
    lines.append("")
    lines.append("static const msf_trig_entry_t MSF_TRIG_PI =")
    pi_line = emit_entry("pi", pi_e, pi_m)
    lines.append(pi_line.replace("},  /*", "}  /*") + ";")
    lines.append("")
    lines.append("static const msf_trig_entry_t MSF_TRIG_SIN_C[MSF_TRIG_NSIN] = {")
    for k, (e, m) in enumerate(sin_entries):
        lines.append(emit_entry(f"1/{2 * k + 1}!", e, m))
    lines.append("};")
    lines.append("")
    lines.append("static const msf_trig_entry_t MSF_TRIG_COS_C[MSF_TRIG_NCOS] = {")
    for k, (e, m) in enumerate(cos_entries):
        lines.append(emit_entry(f"1/{2 * k}!", e, m))
    lines.append("};")
    lines.append("")
    lines.append("#endif /* MSF_TRIG_TABLES_H */")
    text = "\n".join(lines) + "\n"
    with open(out_path, "w", newline="\n") as fh:
        fh.write(text)
    print(f"wrote {out_path}: pi + {n_sin_max} sin + {n_cos_max} cos entries; "
          f"stage terms sin={ns} delta={nd}; tails sin={ts} delta={td}")


if __name__ == "__main__":
    main()
