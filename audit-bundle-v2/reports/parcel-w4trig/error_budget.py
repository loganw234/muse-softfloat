"""Error-budget derivation for the w4trig interval kernel.

Design being budgeted (ledger design entry): positive wide
floats, W-bit normalized significands over 32-bit limbs, every
kernel quantity an interval [lo, hi] with outward rounding.
Coefficients and pi are stored floored at the widest stage; at
any stage the coefficient interval is [trunc_W(c), trunc_W(c)
+ 1 ulp_W]. Horner evaluates the alternating Taylor series in
z = u^2 from the smallest term; u = pi * t, t exact dyadic,
0 <= t <= 1/4, so 0 <= u <= pi/4 and 0 <= z <= (pi/4)^2.

This script derives, per stage width W in {160, 256, 384}:
  * term counts such that the alternating Taylor tail is below
    2^-(W+24) absolute at z_max (first neglected term times
    1/(1-ratio), ratio bounded at z_max);
  * a rigorous upper bound Ek(W) on the relative interval
    half-width (hi-lo)/(2*value) of sin(u), cos(u) (delta
    form), by width recurrence:
      mul:  w' <= w_a + w_b + w_a*w_b + 2*2^(1-W)
            (outward rounding moves each endpoint by at most
            1 ulp; ulp/value <= 2^(1-W) for value in [2^e, 2^e+1))
      sub a-b, b <= rho*a, rho<1:
            w' <= (w_a + rho*w_b)/(1-rho) + 2*2^(1-W)/(1-rho)
      coefficient / pi interval: w0 <= 2^(1-W) (one ulp wide)
      tail: added as absolute widening, converted with the
            range lower bounds S>=0.9003, C>=0.7071, D>=0.9496.
      Horner step for term k (sin):  acc <- c_k - z*acc,
            rho_k <= z_max/((2k+2)(2k+3)) because
            z*acc_{k+1} <= z*c_{k+1} and c_{k+1}/c_k is that.
            (cos: c_k = 1/(2k)!, rho_k <= z/((2k+1)(2k+2));
            delta D: d_k = 2/(2k+2)!, same ratios as cos shifted.)
All bounds computed in exact Fractions with pi bounded above
by a 60-digit rational ceiling.
"""
from fractions import Fraction
import math

# pi < 3.141592653589793238462643383279502884197169399375105820974945
PI_HI = Fraction(314159265358979323846264338327950288419716939937511, 10**50)
ZMAX = (PI_HI / 4) ** 2
S_MIN = Fraction(9003, 10000)      # sin(u)/u on [0, pi/4]
C_MIN = Fraction(7071, 10000)      # cos(u) on [0, pi/4]
D_MIN = Fraction(9496, 10000)      # 2(1-cos u)/u^2 on [0, pi/4]


def tail_terms(kind, target_bits):
    """Smallest N with alternating tail after N terms (k=0..N-1)
    <= 2^-target_bits absolute at z=ZMAX. Returns (N, bound)."""
    # term_k magnitude: sin S: z^k/(2k+1)! ; cos C: z^k/(2k)! ;
    # delta D: 2 z^k/(2k+2)!
    k = 0
    while True:
        if kind == "sin":
            term = ZMAX**k / Fraction(math.factorial(2 * k + 1))
            ratio = ZMAX / Fraction((2 * k + 2) * (2 * k + 3))
        elif kind == "cos":
            term = ZMAX**k / Fraction(math.factorial(2 * k))
            ratio = ZMAX / Fraction((2 * k + 1) * (2 * k + 2))
        else:  # delta D coefficients 2/(2k+2)!
            term = 2 * ZMAX**k / Fraction(math.factorial(2 * k + 2))
            ratio = ZMAX / Fraction((2 * k + 3) * (2 * k + 4))
        bound = term / (1 - ratio)
        if bound <= Fraction(1, 2**target_bits):
            return k, bound  # N = k terms kept (0..k-1), tail from k
        k += 1


def mul_w(wa, wb, W):
    eps = Fraction(2, 2**W)  # 2^(1-W)
    return wa + wb + wa * wb + 2 * eps


def horner_width(kind, nterms, wz, W, tail_abs, val_min):
    eps = Fraction(2, 2**W)
    w = eps  # top coefficient interval, one ulp
    for k in range(nterms - 2, -1, -1):
        if kind == "sin":
            rho = ZMAX / Fraction((2 * k + 2) * (2 * k + 3))
        elif kind == "cos":
            rho = ZMAX / Fraction((2 * k + 1) * (2 * k + 2))
        else:
            rho = ZMAX / Fraction((2 * k + 3) * (2 * k + 4))
        wprod = mul_w(wz, w, W)
        # acc = c_k - prod, c_k width eps; prod <= rho * c_k
        w = (eps + rho * wprod) / (1 - rho) + 2 * eps / (1 - rho)
    return w + tail_abs / val_min


def log2fr(x):
    return math.log2(float(x)) if x > 0 else float("-inf")


def scalar_ek(W, n_sin, n_del, tail_sin, tail_del):
    """Scalar (single-value) evaluation with truncating wide
    ops: relative-error recurrence. One truncating op or one
    truncated constant errs by <= eps = 2^(1-W) relative."""
    eps = Fraction(2, 2**W)
    e_u = eps + eps + eps * eps          # pi trunc + mul trunc
    e_z = 2 * e_u + e_u * e_u + eps

    def horner(kind, nterms, tail_abs, val_min):
        e = eps
        for k in range(nterms - 2, -1, -1):
            if kind == "sin":
                rho = ZMAX / Fraction((2 * k + 2) * (2 * k + 3))
            else:
                rho = ZMAX / Fraction((2 * k + 3) * (2 * k + 4))
            e_prod = e_z + e + e_z * e + eps
            e = (eps + rho * e_prod) / (1 - rho) + eps
        return e + tail_abs / val_min

    e_s = horner("sin", n_sin, tail_sin, S_MIN)
    e_sin = e_u + e_s + e_u * e_s + eps
    e_d = horner("delta", n_del, tail_del, D_MIN)
    e_delta = e_z + e_d + e_z * e_d + eps
    return e_sin, e_delta


for W in (160, 256, 384):
    eps = Fraction(2, 2**W)
    n_sin, tail_sin = tail_terms("sin", W + 24)
    n_cos, tail_cos = tail_terms("cos", W + 24)
    n_del, tail_del = tail_terms("delta", W + 24)
    w_pi = eps
    w_u = mul_w(w_pi, Fraction(0), W)       # t exact
    w_z = mul_w(w_u, w_u, W)
    w_s = horner_width("sin", n_sin, w_z, W, tail_sin, S_MIN)
    w_sin = mul_w(w_u, w_s, W)               # sin(u) = u*S(z)
    w_c = horner_width("cos", n_cos, w_z, W, tail_cos, C_MIN)
    w_d = horner_width("delta", n_del, w_z, W, tail_del, D_MIN)
    w_delta = mul_w(w_z, w_d, W)             # delta=(z/2)*D; /2 exact
    print(f"W={W}: terms sin={n_sin} cos={n_cos} delta={n_del}")
    print(f"  tails: sin<=2^{log2fr(tail_sin):.1f} cos<=2^{log2fr(tail_cos):.1f}"
          f" delta<=2^{log2fr(tail_del):.1f} (target 2^-{W+24})")
    print(f"  widths: w_u<=2^{log2fr(w_u):.2f} w_z<=2^{log2fr(w_z):.2f}")
    print(f"  E_sin rel half-width <= 2^{log2fr(w_sin/2):.2f} (full 2^{log2fr(w_sin):.2f})")
    print(f"  E_cos(direct)        <= 2^{log2fr(w_c/2):.2f}")
    print(f"  E_delta relative     <= 2^{log2fr(w_delta/2):.2f}")
    ek = max(w_sin, w_c, w_delta)
    print(f"  Ek(W) full-width bound = 2^{log2fr(ek):.2f}")
    es, ed = scalar_ek(W, n_sin, n_del, tail_sin, tail_del)
    print(f"  SCALAR Ek: sin<=2^{log2fr(es):.2f} delta<=2^{log2fr(ed):.2f}")


def _scalar_tails():
    pass
print("z_max =", float(ZMAX))
