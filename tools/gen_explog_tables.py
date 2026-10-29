#!/usr/bin/env python3
"""Generate src/msf_explog_tables.h for the exp2/exp2m1 kernel.

First principles only (trig-generator pattern): Taylor
coefficients are the exact rationals 1/k!; ln2 is computed
with mpmath at 260-digit precision and floored to 384-bit
limbs by exact rational arithmetic, the floor proven stable
by checking that a +-2^-590 bracket around the computed
value floors to the same 384-bit integer (computation at
~865-bit precision, cross-checked at a second precision;
measured agreement printed). Every stored entry is the
exact floor of the true constant at 384 bits: stored <=
true < stored + 1 ulp, verified per entry with Fractions
(ln2 against the bracket). Stage term counts make both
Taylor tails <= 2^-(W+24) by exact-rational geometric
bounds at U = ln2/2 (U itself the bracket hi endpoint over
2). The Ek exponents are integers proven here by the
scalar recurrence of ledger/parcel-w5exp2.md Sec. 5 (one
truncating op or truncated constant <= 2^(1-W) relative,
Horner weights from the same geometric bounds, 9-bit
reserve as in the trig generator) and printed at
generation time; a hand-narrowed header fails byte
comparison against regeneration. No decimal literals are
emitted.

Usage: gen_explog_tables.py OUT.h
"""
import math
import sys
from fractions import Fraction

import mpmath

W_TOP = 384
LIMBS = W_TOP // 32
STAGE_LIMBS = (5, 8, 12)


def floor_entry(v: Fraction):
    """Exact floor of positive Fraction v to a W_TOP-bit
    normalized significand: (e, M) with
    M * 2^(e-(W_TOP-1)) <= v < (M+1) * 2^(e-(W_TOP-1))."""
    assert v > 0
    e = v.numerator.bit_length() - v.denominator.bit_length()
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


def ln2_fraction(dps):
    mpmath.mp.dps = dps
    v = mpmath.mp.log(2)
    sign, man, exp, _bc = v._mpf_
    assert sign == 0
    return Fraction(man) * Fraction(2) ** exp


def ln2_bracket():
    a = ln2_fraction(260)
    b = ln2_fraction(210)
    diff = abs(a - b)
    print(f"# ln2: |dps260-dps210| ~= 2^{math.log2(float(diff)):.1f}")
    assert diff < Fraction(2) ** -600
    bracket = Fraction(2) ** -590
    e1, m1 = floor_entry(a - bracket)
    e2, m2 = floor_entry(a + bracket)
    assert (e1, m1) == (e2, m2), "ln2 floor not bracket-stable"
    # U := (ln2 hi)/2 >= |u|; (a, bracket) for reciprocal floors
    return (e1, m1), (a + bracket) / 2, a, bracket


def recip_floor(a, bracket, scale):
    """384-bit floor of scale/ln2, proven bracket-stable:
    true ln2 in [a-bracket, a+bracket] puts scale/ln2 in
    [scale/(a+bracket), scale/(a-bracket)]; both ends must
    floor to the same entry."""
    e1, m1 = floor_entry(scale / (a + bracket))
    e2, m2 = floor_entry(scale / (a - bracket))
    assert (e1, m1) == (e2, m2), f"{scale}/ln2 floor unstable"
    return e1, m1


def bits_of(bound):
    bits = 0
    while Fraction(2) ** -(bits + 1) >= bound:
        bits += 1
    assert bits > 40
    return bits - 9


def tail_exp(u, k):
    return u**k / Fraction(math.factorial(k)) / (1 - u / Fraction(k + 1))


def tail_m(u, k):
    return u**k / Fraction(math.factorial(k + 1)) / (1 - u / Fraction(k + 2))


def terms_for(u, w):
    k = 1
    while True:
        if (tail_exp(u, k) <= Fraction(2) ** -(w + 24)
                and tail_m(u, k) <= Fraction(2) ** -(w + 24)):
            return k
        k += 1


def ek_exp(u, w, kterms):
    """Relative-error bound for the scalar truncating
    evaluations (exp Horner and z*M(z)), as a bit count B
    with Ek <= 2^-B after the 9-bit reserve. Recurrence of
    ledger/parcel-w5exp2.md Sec. 5."""
    eps = Fraction(2, 2**w)
    e_u = 2 * eps + eps * eps
    e = eps
    for k in range(kterms - 2, -1, -1):
        rho = u / (Fraction(k + 1) * (1 - u / Fraction(k + 2)))
        e_prod = e_u + e + e_u * e + eps
        e = eps + rho * e_prod + eps
    e_v = e + tail_exp(u, kterms)
    e = eps
    for j in range(kterms - 1, 0, -1):
        rho = u / (Fraction(j + 2) * (1 - u / Fraction(j + 3)))
        e_prod = e_u + e + e_u * e + eps
        e = eps + rho * e_prod + eps
    e_m = e_u + e + e_u * e + eps + tail_m(u, kterms)
    # Delta form D(z) = sum (-z)^k/(k+1)! (alternating,
    # decreasing terms): Horner partials are positive with
    # P_k >= c_{k+1} (1 - rho_k), hence the trig generator's
    # (eps + rho e_prod)/(1 - rho) shape. delta = z * D(z),
    # D(z) >= 1 - z/2 >= 1 - U/2; alternating tail bounded by
    # its first omitted term.
    d_min = 1 - u / 2
    e = eps
    for j in range(kterms - 1, 0, -1):
        rho = u / (Fraction(j + 2) * (1 - u / Fraction(j + 3)))
        e_prod = e_u + e + e_u * e + eps
        e = (eps + rho * e_prod) / (1 - rho) + eps
    tail_d = u**kterms / Fraction(math.factorial(kterms + 1))
    e_d = e_u + e + e_u * e + eps + tail_d / d_min
    bound = max(e_v, e_m, e_d)
    bits = 0
    while Fraction(2) ** -(bits + 1) >= bound:
        bits += 1
    assert bits > 40
    return bits - 9


# ---- log2/log2p1 (SF-2 Step 3b, ledger/parcel-w5log2.md) ----
# |s| <= (sqrt2-1)/(sqrt2+1): sqrt2 < 14143/10000 (integer
# check below) and s increasing in mm give the rational
# ceiling SRAT; the low side follows by |s(mm)|=|s(1/mm)|.
assert 14143 * 14143 > 2 * 10000 * 10000
SRAT = Fraction(14143 - 10000, 14143 + 10000)
XRAT = Fraction(1, 256)  # tiny-path |x| ceiling bound


def tail_a(z, j):
    return z**j / (Fraction(2 * j + 1) * (1 - z))


def terms_log(z, w):
    j = 1
    while tail_a(z, j) > Fraction(2) ** -(w + 24):
        j += 1
    return j


def ek_log(z, w, jterms):
    """Relative bound for |t| = (2/ln2) * s * A(s^2) with
    s from the floor-exact wide division. Lines per design
    Sec. 5: L_sticky (NUM/DEN wf truncations), L_div, L_z,
    L_A (Horner + tail), L_C (constant + final muls)."""
    eps = Fraction(2, 2**w)
    # L_sticky: wf_normalize truncation of NUM/DEN. Shipped
    # big_top_bit is a bit LENGTH, so a normalized wf
    # significand can sit in [2^(W-2), 2^(W-1)): dropped
    # bits are < 2^-(W-2) = 2*eps relative per conversion
    # (probe-verified in the parcel; shipped parcels never
    # truncated through wf_normalize - this line is new).
    e_nd = 2 * eps
    rel_nd = 2 * e_nd / (1 - e_nd)        # (1+e)/(1-e) - 1
    e_s = rel_nd + eps + rel_nd * eps     # + division floor
    e_z = 2 * e_s + e_s * e_s + eps
    e = eps
    for j in range(jterms - 2, -1, -1):
        rho = z * Fraction(2 * j + 1) / (Fraction(2 * j + 3) * (1 - z))
        e_prod = e_z + e + e_z * e + eps
        e = eps + rho * e_prod + eps
    e_a = e + tail_a(z, jterms)           # A >= 1
    m1 = eps + e_s + eps * e_s + eps      # C2 floor, s, mul
    e_t = m1 + e_a + m1 * e_a + eps       # final mul by A
    return bits_of(e_t)


def tail_bp(x, j):
    return x**j / (Fraction(j + 1) * (1 - x))


def tail_bm(x, j):
    return x**j / Fraction(j + 1)


def terms_tiny(x, w):
    j = 1
    while max(tail_bp(x, j), tail_bm(x, j)) / (1 - x) \
            > Fraction(2) ** -(w + 24):
        j += 1
    return j


def ek_tiny(x, w, jterms):
    """Relative bound for Q = |x| * (1/ln2) * B(|x|), x
    exact in wf. Both B shapes (positive for x<0 original,
    alternating for x>0); tails relativized by B >= 1-X."""
    eps = Fraction(2, 2**w)
    e = eps
    for j in range(jterms - 2, -1, -1):
        rho = x * Fraction(j + 1) / (Fraction(j + 2) * (1 - x))
        e = eps + rho * (e + eps) + eps
    e_bp = e + tail_bp(x, jterms) / (1 - x)
    e = eps
    for j in range(jterms - 2, -1, -1):
        rho = x * Fraction(j + 1) / (Fraction(j + 2) * (1 - x))
        e = (eps + rho * (e + eps)) / (1 - rho) + eps
    e_bm = e + tail_bm(x, jterms) / (1 - x)
    e_b = max(e_bp, e_bm)
    m1 = 2 * eps                          # x exact, C1, mul
    e_q = m1 + e_b + m1 * e_b + eps
    return bits_of(e_q)


def emit_entry(name, e, m):
    limbs = [(m >> (32 * i)) & 0xFFFFFFFF for i in range(LIMBS)]
    body = ", ".join(f"0x{x:08x}u" for x in limbs)
    return f"    {{ {e}, {{ {body} }} }},  /* {name} */"


def main():
    out_path = sys.argv[1]
    (ln2_e, ln2_m), u, ln2_a, ln2_br = ln2_bracket()
    assert u < Fraction(34658, 100000)
    stage_terms = [terms_for(u, 32 * lb) for lb in STAGE_LIMBS]
    kmax = max(stage_terms)
    # EXP_C[k] = 1/k! for k = 0..kmax (M Horner reaches c_kmax)
    entries = [floor_entry(Fraction(1, math.factorial(k)))
               for k in range(kmax + 1)]
    ek = [ek_exp(u, 32 * lb, kt)
          for lb, kt in zip(STAGE_LIMBS, stage_terms)]
    print(f"# stage terms: {stage_terms}; Ek exponents "
          f"(9-bit reserve): {ek}")
    # log2/log2p1 additions (Step 3b)
    zrat = SRAT * SRAT
    assert zrat < Fraction(295, 10000)
    inv_e, inv_m = recip_floor(ln2_a, ln2_br, Fraction(1))
    two_e, two_m = recip_floor(ln2_a, ln2_br, Fraction(2))
    log_terms = [terms_log(zrat, 32 * lb) for lb in STAGE_LIMBS]
    tiny_terms = [terms_tiny(XRAT, 32 * lb) for lb in STAGE_LIMBS]
    ek_l = [ek_log(zrat, 32 * lb, jt)
            for lb, jt in zip(STAGE_LIMBS, log_terms)]
    ek_t = [ek_tiny(XRAT, 32 * lb, jt)
            for lb, jt in zip(STAGE_LIMBS, tiny_terms)]
    ac = [floor_entry(Fraction(1, 2 * j + 1))
          for j in range(max(log_terms))]
    pc = [floor_entry(Fraction(1, j + 1))
          for j in range(max(tiny_terms))]
    print(f"# log terms: {log_terms}; EK_LOG: {ek_l}; "
          f"tiny terms: {tiny_terms}; EK_TINY: {ek_t}")

    lines = []
    lines.append("/* msf_explog_tables.h - GENERATED by "
                 "tools/gen_explog_tables.py;")
    lines.append(" * do not edit. Each entry is the exact 384-bit floor of")
    lines.append(" * the named constant: value in [M, M+1) * 2^(e-383),")
    lines.append(" * M the 12 little-endian limbs. */")
    lines.append("#ifndef MSF_EXPLOG_TABLES_H")
    lines.append("#define MSF_EXPLOG_TABLES_H")
    lines.append("")
    lines.append("#include <stdint.h>")
    lines.append("")
    lines.append("#define MSF_EXPLOG_WTOP 384")
    lines.append("#define MSF_EXPLOG_MAXL 12")
    lines.append("")
    lines.append("typedef struct msf_explog_entry {")
    lines.append("    int32_t e;")
    lines.append("    uint32_t m[MSF_EXPLOG_MAXL];")
    lines.append("} msf_explog_entry_t;")
    lines.append("")
    sl = ", ".join(str(x) for x in STAGE_LIMBS)
    lines.append(f"static const int MSF_EXPLOG_STAGE_LIMBS[3] = {{ {sl} }};")
    nt = ", ".join(str(x) for x in stage_terms)
    lines.append(f"static const int MSF_EXPLOG_NTERMS[3] = {{ {nt} }};")
    ek_s = ", ".join(str(x) for x in ek)
    lines.append(f"static const int MSF_EXPLOG_EK_EXP[3] = {{ {ek_s} }};")
    lt = ", ".join(str(x) for x in log_terms)
    lines.append(f"static const int MSF_EXPLOG_NTERMS_LOG[3] = {{ {lt} }};")
    ekl = ", ".join(str(x) for x in ek_l)
    lines.append(f"static const int MSF_EXPLOG_EK_LOG[3] = {{ {ekl} }};")
    tt = ", ".join(str(x) for x in tiny_terms)
    lines.append(f"static const int MSF_EXPLOG_NTERMS_TINY[3] = {{ {tt} }};")
    ekt = ", ".join(str(x) for x in ek_t)
    lines.append(f"static const int MSF_EXPLOG_EK_TINY[3] = {{ {ekt} }};")
    lines.append("")
    lines.append(f"#define MSF_EXPLOG_NC {kmax + 1}")
    lines.append("")
    lines.append("static const msf_explog_entry_t MSF_EXPLOG_LN2 =")
    ln2_line = emit_entry("ln2", ln2_e, ln2_m)
    lines.append(ln2_line.replace("},  /*", "}  /*") + ";")
    lines.append("")
    lines.append("static const msf_explog_entry_t "
                 "MSF_EXPLOG_C[MSF_EXPLOG_NC] = {")
    for k, (e, m) in enumerate(entries):
        lines.append(emit_entry(f"1/{k}!", e, m))
    lines.append("};")
    lines.append("")
    lines.append(f"#define MSF_EXPLOG_NAC {len(ac)}")
    lines.append(f"#define MSF_EXPLOG_NPC {len(pc)}")
    lines.append("")
    lines.append("static const msf_explog_entry_t MSF_EXPLOG_INV_LN2 =")
    il = emit_entry("1/ln2", inv_e, inv_m)
    lines.append(il.replace("},  /*", "}  /*") + ";")
    lines.append("")
    lines.append("static const msf_explog_entry_t "
                 "MSF_EXPLOG_TWO_OVER_LN2 =")
    tl = emit_entry("2/ln2", two_e, two_m)
    lines.append(tl.replace("},  /*", "}  /*") + ";")
    lines.append("")
    lines.append("static const msf_explog_entry_t "
                 "MSF_EXPLOG_AC[MSF_EXPLOG_NAC] = {")
    for j, (e, m) in enumerate(ac):
        lines.append(emit_entry(f"1/{2 * j + 1}", e, m))
    lines.append("};")
    lines.append("")
    lines.append("static const msf_explog_entry_t "
                 "MSF_EXPLOG_PC[MSF_EXPLOG_NPC] = {")
    for j, (e, m) in enumerate(pc):
        lines.append(emit_entry(f"1/{j + 1}", e, m))
    lines.append("};")
    lines.append("")
    lines.append("#endif /* MSF_EXPLOG_TABLES_H */")
    text = "\n".join(lines) + "\n"
    with open(out_path, "w", newline="\n") as fh:
        fh.write(text)
    print(f"wrote {out_path}: ln2 + {kmax + 1} factorial entries; "
          f"stage terms={nt}; Ek={ek_s}; +1/ln2, 2/ln2, "
          f"{len(ac)} atanh, {len(pc)} p1 entries; "
          f"log terms={lt}; EK_LOG={ekl}; tiny terms={tt}; "
          f"EK_TINY={ekt}")


if __name__ == "__main__":
    main()
