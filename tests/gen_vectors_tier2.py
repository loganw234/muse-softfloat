#!/usr/bin/env python3
"""Fresh exact reference + vectors for SF-1 Step 1 (9.6/9.7).

Independent bit/class reference for the 33 Tier 2 rows of the
w4-minmax brief: expectations are computed from the field
definitions with exact rationals for finite values. No shipped
generator's expectation logic is imported. Provenance family:
exact-py-t2:* (one family for this generator).

Semantics restated from the brief's frozen pins (survey 4.1/4.2):
9.6 selects an operand by value or magnitude (value tie-break),
-0 is the minimum and +0 the maximum, equal values deliver the
first operand; plain forms deliver any NaN per the SF-0 2.5
matrix, Number forms deliver the number for a single NaN (a
signaling NaN still signals invalid) and the matrix for two.
9.7 payload = trailing bits below the quiet bit; getPayload
delivers it as an exact non-negative integer (-1 for non-NaN);
setters build a positive NaN for admissible integral operands
(quiet 0..max, signaling 1..max, -0 admissible-as-0 for the
quiet form only) and +0 otherwise, never signaling.

Usage:
  gen_vectors_tier2.py directed OUTDIR            committed sets
  gen_vectors_tier2.py payload-f16-exhaustive OUT all 65536 encodings
  gen_vectors_tier2.py minmax-f16-sweep OUT       boundary-first sweeps
  gen_vectors_tier2.py seeded OUT [N]             binary32/64 sweeps
"""
import random
import sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

FMTS = {  # name: (bits, exponent field width)
    "f16": (16, 5),
    "f32": (32, 8),
    "f64": (64, 11),
}
INVALID = 0x01

MINMAX_OPS = {  # suffix: (want_min, by_magnitude, is_number)
    "minimum": (True, False, False),
    "maximum": (False, False, False),
    "minimum_number": (True, False, True),
    "maximum_number": (False, False, True),
    "minimum_magnitude": (True, True, False),
    "maximum_magnitude": (False, True, False),
    "minimum_magnitude_number": (True, True, True),
    "maximum_magnitude_number": (False, True, True),
}
PAYLOAD_OPS = ["get_payload", "set_payload", "set_payload_signaling"]


@lru_cache(maxsize=None)
def params(fmt):
    bits, w = FMTS[fmt]
    t = bits - 1 - w
    return {
        "bits": bits, "w": w, "t": t, "p": t + 1,
        "bias": (1 << (w - 1)) - 1,
        "emaxf": (1 << w) - 1,
        "sign": 1 << (bits - 1),
        "fracmask": (1 << t) - 1,
        "qbit": 1 << (t - 1),
        "inf": ((1 << w) - 1) << t,
        "paybits": t - 1,
        "paymax": (1 << (t - 1)) - 1,
    }


def fields(fmt, x):
    q = params(fmt)
    return ((x >> (q["bits"] - 1)) & 1,
            (x >> q["t"]) & q["emaxf"],
            x & q["fracmask"], q)


@lru_cache(maxsize=None)
def kind_of(fmt, x):
    sign, e, frac, q = fields(fmt, x)
    if e == q["emaxf"]:
        if frac == 0:
            return "inf", sign
        return ("qnan" if frac & q["qbit"] else "snan"), sign
    if e == 0:
        return ("zero" if frac == 0 else "sub"), sign
    return "normal", sign


@lru_cache(maxsize=None)
def finite_value(fmt, x):
    """Exact signed value of a finite encoding, else None."""
    sign, e, frac, q = fields(fmt, x)
    if e == q["emaxf"]:
        return None
    if e == 0:
        sig, exp = frac, 1 - q["bias"] - q["t"]
    else:
        sig, exp = frac | (1 << q["t"]), e - q["bias"] - q["t"]
    v = Fraction(sig) * Fraction(2) ** exp
    return -v if sign else v


def value_cmp(fmt, a, b):
    """9.6 value order on non-NaN operands: -0 below +0."""
    ka, sa = kind_of(fmt, a)
    kb, sb = kind_of(fmt, b)
    if ka == "inf" or kb == "inf":
        if ka == kb:
            return 0 if sa == sb else (-1 if sa else 1)
        if ka == "inf":
            return -1 if sa else 1
        return 1 if sb else -1
    if ka == "zero" and kb == "zero":
        return 0 if sa == sb else (-1 if sa else 1)
    va, vb = finite_value(fmt, a), finite_value(fmt, b)
    return (va > vb) - (va < vb)


def mag_cmp(fmt, a, b):
    ka, _ = kind_of(fmt, a)
    kb, _ = kind_of(fmt, b)
    if ka == "inf" or kb == "inf":
        return 0 if ka == kb else (1 if ka == "inf" else -1)
    va = abs(finite_value(fmt, a))
    vb = abs(finite_value(fmt, b))
    return (va > vb) - (va < vb)


def nan_delivery(fmt, a, b):
    """SF-0 2.5 matrix, same format: (bits, flags)."""
    q = params(fmt)
    for x in (a, b):
        if kind_of(fmt, x)[0] == "snan":
            return x | q["qbit"], INVALID
    for x in (a, b):
        if kind_of(fmt, x)[0] == "qnan":
            return x, 0
    raise AssertionError("nan_delivery with no NaN operand")


def minmax_ref(fmt, op, a, b):
    want_min, by_mag, is_number = MINMAX_OPS[op]
    ka, kb = kind_of(fmt, a)[0], kind_of(fmt, b)[0]
    an, bn = ka in ("qnan", "snan"), kb in ("qnan", "snan")
    if is_number and an != bn:
        flags = INVALID if (ka if an else kb) == "snan" else 0
        return (b if an else a), flags
    if an or bn:
        return nan_delivery(fmt, a, b)
    if by_mag:
        mc = mag_cmp(fmt, a, b)
        if mc != 0:
            pick_a = mc < 0 if want_min else mc > 0
            return (a if pick_a else b), 0
    vc = value_cmp(fmt, a, b)
    pick_a = vc <= 0 if want_min else vc >= 0  # first wins ties
    return (a if pick_a else b), 0


def encode_int(fmt, k):
    """Exact encoding of a non-negative integer k < 2^p."""
    q = params(fmt)
    assert 0 <= k < (1 << q["p"]), k
    if k == 0:
        return 0
    bl = k.bit_length()
    efield = q["bias"] + bl - 1
    frac = (k << (q["t"] - (bl - 1))) & q["fracmask"]
    bits = (efield << q["t"]) | frac
    assert finite_value(fmt, bits) == Fraction(k)  # exact by construction
    return bits


def get_payload_ref(fmt, a):
    q = params(fmt)
    if kind_of(fmt, a)[0] not in ("qnan", "snan"):
        return q["sign"] | encode_int(fmt, 1)  # -1
    return encode_int(fmt, a & (q["qbit"] - 1))


def set_payload_ref(fmt, a, signaling):
    q = params(fmt)
    v = finite_value(fmt, a)
    if v is None or v < 0 or v.denominator != 1:
        return 0
    k = int(v)
    if k > q["paymax"] or (signaling and k == 0):
        return 0
    return q["inf"] | (0 if signaling else q["qbit"]) | k


def payload_ref(fmt, op, a):
    if op == "get_payload":
        return get_payload_ref(fmt, a)
    return set_payload_ref(fmt, a, op == "set_payload_signaling")


def mk(fmt, sign, efield, frac):
    q = params(fmt)
    return (sign << (q["bits"] - 1)) | (efield << q["t"]) | frac


def qnan(fmt, sign, payload):
    q = params(fmt)
    return mk(fmt, sign, q["emaxf"], q["qbit"] | payload)


def snan(fmt, sign, payload):
    return mk(fmt, sign, params(fmt)["emaxf"], payload)


def operand_pool(fmt):
    """Every class x sign with several magnitude relations."""
    q = params(fmt)
    b, t = q["bias"], q["t"]
    pat = 0x155 & q["paymax"] or 1
    pool = [0, q["sign"], q["inf"], q["sign"] | q["inf"]]
    for mag in (mk(fmt, 0, b, 0),              # 1
                mk(fmt, 0, b + 1, 0),          # 2
                mk(fmt, 0, b - 1, 0),          # 1/2
                mk(fmt, 0, 0, 1),              # smallest subnormal
                mk(fmt, 0, 0, q["fracmask"]),  # largest subnormal
                mk(fmt, 0, 1, 0),              # smallest normal
                mk(fmt, 0, q["emaxf"] - 1, q["fracmask"])):  # max finite
        pool += [mag, mag | q["sign"]]
    pool += [qnan(fmt, 0, 0), qnan(fmt, 1, 0), qnan(fmt, 0, 1),
             qnan(fmt, 1, q["paymax"]), qnan(fmt, 0, pat),
             snan(fmt, 0, 1), snan(fmt, 1, 1),
             snan(fmt, 0, q["paymax"]), snan(fmt, 1, pat)]
    seen, out = set(), []
    for x in pool:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def setter_inputs(fmt):
    """Boundary integral/non-integral operand patterns for 9.7."""
    q = params(fmt)
    b, mx = q["bias"], q["paymax"]
    vals = [encode_int(fmt, k) for k in
            (0, 1, 2, 3, mx - 1, mx, mx + 1, 1 << (q["p"] - 1))]
    one = mk(fmt, 0, b, 0)
    vals += [q["sign"], q["sign"] | one, q["sign"] | mk(fmt, 0, b + 1, 0),
             mk(fmt, 0, b - 1, 0),                       # 1/2
             mk(fmt, 0, b, q["qbit"]),                   # 3/2
             q["sign"] | mk(fmt, 0, b - 1, 0),           # -1/2
             mk(fmt, 0, b, 1),                           # 1 + ulp
             mk(fmt, 0, 0, 1), mk(fmt, 1, 0, 1),         # subnormals
             mk(fmt, 0, 0, q["fracmask"]),
             mk(fmt, 0, 1, 0),                           # smallest normal
             mk(fmt, 0, q["emaxf"] - 1, q["fracmask"]),  # max finite
             q["inf"], q["sign"] | q["inf"]]
    seen, out = set(), []
    for x in vals:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def opname(fmt, op):
    return "msf%s_%s" % (fmt[1:], op)


def write_lines(path, header, lines):
    with open(path, "w", newline="\n") as f:
        if header:
            f.write(header)
        f.writelines(lines)
    print("wrote %s (%d cases)" % (path, len(lines)))


HEADER = "# generated by tests/gen_vectors_tier2.py - do not edit (regenerate)\n"


def directed(outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for fmt in FMTS:
        pool = operand_pool(fmt)
        lines = []
        for op in MINMAX_OPS:
            for a in pool:
                for b in pool:
                    r, fl = minmax_ref(fmt, op, a, b)
                    lines.append("%s - %x %x -> %x %02x "
                                 "exact-py-t2:directed-minmax\n"
                                 % (opname(fmt, op), a, b, r, fl))
        write_lines(outdir / ("minmax-%s.vec" % fmt), HEADER, lines)
        inputs = list(dict.fromkeys(pool + setter_inputs(fmt)))
        lines = []
        for op in PAYLOAD_OPS:
            for a in inputs:
                r = payload_ref(fmt, op, a)
                lines.append("%s - %x -> %x -- "
                             "exact-py-t2:directed-payload\n"
                             % (opname(fmt, op), a, r))
        write_lines(outdir / ("payload-%s.vec" % fmt), HEADER, lines)


def payload_f16_exhaustive(out):
    fmt = "f16"
    q = params(fmt)
    # Reference round-trips, asserted here; the C composition then
    # holds transitively because every setter result encoding also
    # appears below as a get_payload / is_signaling argument.
    for k in range(q["paymax"] + 1):
        enc = encode_int(fmt, k)
        assert payload_ref(fmt, "get_payload",
                           payload_ref(fmt, "set_payload", enc)) == enc
        if k >= 1:
            assert payload_ref(fmt, "get_payload",
                               payload_ref(fmt, "set_payload_signaling",
                                           enc)) == enc
    print("reference round-trips: set_payload %d, "
          "set_payload_signaling %d"
          % (q["paymax"] + 1, q["paymax"]))
    with open(out, "w", newline="\n") as f:
        n = 0
        for op in PAYLOAD_OPS:
            nm = opname(fmt, op)
            for a in range(65536):
                f.write("%s - %x -> %x -- "
                        "exact-py-t2:payload-f16-exhaustive\n"
                        % (nm, a, payload_ref(fmt, op, a)))
                n += 1
        for k in range(q["paymax"] + 1):
            enc = encode_int(fmt, k)
            r = payload_ref(fmt, "set_payload", enc)
            f.write("msf16_is_signaling - %x -> 0 -- "
                    "exact-py-t2:payload-f16-exhaustive\n" % r)
            n += 1
            if k >= 1:
                r = payload_ref(fmt, "set_payload_signaling", enc)
                f.write("msf16_is_signaling - %x -> 1 -- "
                        "exact-py-t2:payload-f16-exhaustive\n" % r)
                n += 1
    print("wrote %s (%d cases)" % (out, n))


def minmax_f16_sweep(out):
    fmt = "f16"
    q = params(fmt)
    b = q["bias"]
    pat = 0x155 & q["paymax"]
    firsts = [q["sign"] | q["inf"],               # -inf
              q["sign"] | mk(fmt, 0, b, 0),      # -1
              q["sign"],                         # -0
              0,                                 # +0
              mk(fmt, 0, b, 0),                  # +1
              q["inf"],                          # +inf
              qnan(fmt, 0, pat),                 # +qNaN(pat)
              snan(fmt, 1, pat)]                 # -sNaN(pat)
    names = [(op, opname(fmt, op)) for op in MINMAX_OPS]
    with open(out, "w", newline="\n") as f:
        n = 0
        for a in firsts:
            for x in range(65536):
                for op, nm in names:
                    r, fl = minmax_ref(fmt, op, a, x)
                    f.write("%s - %x %x -> %x %02x "
                            "exact-py-t2:minmax-f16-sweep\n"
                            % (nm, a, x, r, fl))
                    n += 1
    print("wrote %s (%d cases, %d first operands x 65536 x %d ops)"
          % (out, n, len(firsts), len(names)))


def random_encoding(rng, fmt):
    q = params(fmt)
    kind = rng.choices(("zero", "sub", "normal", "inf", "qnan", "snan"),
                       weights=(1, 3, 10, 1, 3, 3))[0]
    sign = rng.randrange(2)
    if kind == "zero":
        return sign << (q["bits"] - 1)
    if kind == "sub":
        return mk(fmt, sign, 0, rng.randrange(1, q["fracmask"] + 1))
    if kind == "normal":
        return mk(fmt, sign, rng.randrange(1, q["emaxf"]),
                  rng.randrange(q["fracmask"] + 1))
    if kind == "inf":
        return mk(fmt, sign, q["emaxf"], 0)
    if kind == "qnan":
        return qnan(fmt, sign, rng.randrange(q["paymax"] + 1))
    return snan(fmt, sign, rng.randrange(1, q["paymax"] + 1))


def seeded(out, npairs=12000):
    rng = random.Random(20261027)  # fixed seed: regenerable sweeps
    with open(out, "w", newline="\n") as f:
        n = 0
        for fmt in ("f32", "f64"):
            q = params(fmt)
            for _ in range(npairs):
                a = random_encoding(rng, fmt)
                b = random_encoding(rng, fmt)
                for op in MINMAX_OPS:
                    r, fl = minmax_ref(fmt, op, a, b)
                    f.write("%s - %x %x -> %x %02x "
                            "exact-py-t2:seeded-sweep\n"
                            % (opname(fmt, op), a, b, r, fl))
                    n += 1
            for _ in range(npairs):
                a = random_encoding(rng, fmt)
                for op in PAYLOAD_OPS:
                    f.write("%s - %x -> %x -- "
                            "exact-py-t2:seeded-sweep\n"
                            % (opname(fmt, op), a, payload_ref(fmt, op, a)))
                    n += 1
            # integral-focused setter/getter encodings near the range
            for _ in range(npairs // 3):
                k = rng.randrange(0, (q["paymax"] + 2) * 2)
                if k >= (1 << q["p"]):
                    continue
                a = encode_int(fmt, k)
                if rng.randrange(4) == 0:
                    a ^= q["sign"]
                for op in PAYLOAD_OPS:
                    f.write("%s - %x -> %x -- "
                            "exact-py-t2:seeded-sweep\n"
                            % (opname(fmt, op), a, payload_ref(fmt, op, a)))
                    n += 1
    print("wrote %s (%d cases)" % (out, n))


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    mode, out = argv[1], argv[2]
    if mode == "directed":
        directed(out)
    elif mode == "payload-f16-exhaustive":
        payload_f16_exhaustive(out)
    elif mode == "minmax-f16-sweep":
        minmax_f16_sweep(out)
    elif mode == "seeded":
        seeded(out, int(argv[3]) if len(argv) > 3 else 12000)
    else:
        print("unknown mode: %s" % mode)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

