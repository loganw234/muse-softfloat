#!/usr/bin/env python3
"""Verifier-w4minmax independent reference, written fresh from the brief
pins (ledger/briefs/w4-minmax.md) and the SF-1 survey paraphrase.
Deliberately structured differently from tests/gen_vectors_tier2.py:
tuple decoding, flag-first helpers, mask-based payload logic.
"""
import random
import sys
from fractions import Fraction

SPECS = {
    "f16": (16, 5),
    "f32": (32, 8),
    "f64": (64, 11),
}
INV = 0x01
WANT = {"minimum": True, "maximum": False, "minimum_number": True,
        "maximum_number": False, "minimum_magnitude": True,
        "maximum_magnitude": False, "minimum_magnitude_number": True,
        "maximum_magnitude_number": False}


def spec(fmt):
    bits, ebits = SPECS[fmt]
    fbits = bits - 1 - ebits
    return {"bits": bits, "ebits": ebits, "fbits": fbits,
            "bias": (1 << (ebits - 1)) - 1,
            "emax": (1 << ebits) - 1,
            "sign": 1 << (bits - 1),
            "fmask": (1 << fbits) - 1,
            "qbit": 1 << (fbits - 1),
            "inf": ((1 << ebits) - 1) << fbits,
            "pbits": fbits - 1,
            "pmax": (1 << (fbits - 1)) - 1}


def decode(fmt, x):
    s = spec(fmt)
    sgn = (x >> (s["bits"] - 1)) & 1
    e = (x >> s["fbits"]) & s["emax"]
    f = x & s["fmask"]
    if e == s["emax"]:
        if f == 0:
            return ("inf", sgn, 0)
        if f & s["qbit"]:
            return ("qnan", sgn, f)
        return ("snan", sgn, f)
    if e == 0:
        if f == 0:
            return ("zero", sgn, 0)
        return ("sub", sgn, f)
    return ("normal", sgn, f)


def exact_value(fmt, x):
    """Exact signed value for finite x, else None."""
    s = spec(fmt)
    cls, sgn, f = decode(fmt, x)
    if cls in ("inf", "qnan", "snan"):
        return None
    e = (x >> s["fbits"]) & s["emax"]
    if e == 0:
        v = Fraction(f, 1 << (s["bias"] - 1 + s["fbits"]))
    else:
        sig = f + (1 << s["fbits"])
        exp = e - s["bias"] - s["fbits"]
        v = Fraction(sig << exp) if exp >= 0 else Fraction(sig, 1 << (-exp))
    return -v if sgn else v


def cmp_value(fmt, a, b):
    """9.6 value order; -0 below +0; first-operand-wins handled by caller."""
    ca, sa, _ = decode(fmt, a)
    cb, sb, _ = decode(fmt, b)
    if ca == "inf" or cb == "inf":
        if ca == cb == "inf":
            return 0 if sa == sb else (-1 if sa else 1)
        if ca == "inf":
            return -1 if sa else 1
        return 1 if sb else -1
    if ca == "zero" and cb == "zero":
        return 0 if sa == sb else (-1 if sa else 1)
    va, vb = exact_value(fmt, a), exact_value(fmt, b)
    return (va > vb) - (va < vb)


def cmp_mag(fmt, a, b):
    s = spec(fmt)
    ma = a & ~s["sign"]
    mb = b & ~s["sign"]
    return (ma > mb) - (ma < mb)


def deliver_matrix(fmt, a, b):
    s = spec(fmt)
    for x in (a, b):
        if decode(fmt, x)[0] == "snan":
            return (x | s["qbit"]) & ((1 << s["bits"]) - 1), INV
    for x in (a, b):
        if decode(fmt, x)[0] == "qnan":
            return x, 0
    raise AssertionError("no NaN")


def ref_minmax(fmt, op, a, b):
    want_min = WANT[op]
    by_mag = "magnitude" in op
    is_num = "number" in op
    ka = decode(fmt, a)[0]
    kb = decode(fmt, b)[0]
    an = ka in ("qnan", "snan")
    bn = kb in ("qnan", "snan")
    if is_num and an != bn:
        single = ka if an else kb
        return (b if an else a), (INV if single == "snan" else 0)
    if an or bn:
        return deliver_matrix(fmt, a, b)
    if by_mag:
        m = cmp_mag(fmt, a, b)
        if m:
            take_a = (m < 0) if want_min else (m > 0)
            return (a if take_a else b), 0
    v = cmp_value(fmt, a, b)
    take_a = (v <= 0) if want_min else (v >= 0)
    return (a if take_a else b), 0


def int_pattern(fmt, k):
    """Exact non-negative integer k < 2^p as same-format pattern."""
    s = spec(fmt)
    assert 0 <= k < (1 << (s["fbits"] + 1)), k
    if k == 0:
        return 0
    bl = k.bit_length()
    ef = s["bias"] + bl - 1
    frac = (k << (s["fbits"] - bl + 1)) & s["fmask"]
    return (ef << s["fbits"]) | frac


def ref_get(fmt, a):
    s = spec(fmt)
    if decode(fmt, a)[0] not in ("qnan", "snan"):
        return s["sign"] | int_pattern(fmt, 1)
    return int_pattern(fmt, a & (s["qbit"] - 1))


def ref_set(fmt, a, signaling):
    s = spec(fmt)
    cls = decode(fmt, a)[0]
    if cls in ("qnan", "snan", "inf"):
        return 0
    v = exact_value(fmt, a)
    if v is None or v < 0 or v.denominator != 1:
        return 0
    k = int(v)
    if k == 0:
        # +0 and -0 both carry value 0; quiet admits, signaling refuses
        return 0 if signaling else s["inf"] | s["qbit"]
    if k > s["pmax"]:
        return 0
    return s["inf"] | (0 if signaling else s["qbit"]) | k


def ref_payload(fmt, op, a):
    if op == "get_payload":
        return ref_get(fmt, a)
    return ref_set(fmt, a, op == "set_payload_signaling")


def opname(fmt, op):
    return "msf%s_%s" % (fmt[1:], op)


def main():
    mode = sys.argv[1]
    if mode == "xcheck-payload-f16":
        # full 65536 x 3 ops: my ref vs copy generator module
        sys.path.insert(0, sys.argv[2] + "/tests")
        import gen_vectors_tier2 as G
        bad = 0
        for a in range(65536):
            for op in ("get_payload", "set_payload", "set_payload_signaling"):
                mine = ref_payload("f16", op, a)
                theirs = G.payload_ref("f16", op, a)
                if mine != theirs:
                    if bad < 10:
                        print("MISMATCH %s %04x mine=%04x theirs=%04x"
                              % (op, a, mine, theirs))
                    bad += 1
        print("payload-f16 xcheck: %d mismatches of 196608" % bad)
    elif mode == "xcheck-minmax-cells":
        # every class-cell representative pair x 8 ops x 3 fmts
        sys.path.insert(0, sys.argv[2] + "/tests")
        import gen_vectors_tier2 as G
        pool = {}
        for fmt in SPECS:
            pool[fmt] = G.operand_pool(fmt)
        ops = ("minimum", "maximum", "minimum_number", "maximum_number",
               "minimum_magnitude", "maximum_magnitude",
               "minimum_magnitude_number", "maximum_magnitude_number")
        bad = tot = 0
        for fmt in SPECS:
            for a in pool[fmt]:
                for b in pool[fmt]:
                    for op in ops:
                        mine, mf = ref_minmax(fmt, op, a, b)
                        theirs, tf = G.minmax_ref(fmt, op, a, b)
                        tot += 1
                        if (mine, mf) != (theirs, tf):
                            if bad < 10:
                                print("MISMATCH %s %s %x %x mine=%x/%02x theirs=%x/%02x"
                                      % (fmt, op, a, b, mine, mf, theirs, tf))
                            bad += 1
        print("minmax cell xcheck: %d mismatches of %d" % (bad, tot))
    elif mode == "gate-payload-f16":
        out = sys.argv[2]
        n = 0
        with open(out, "w", newline="\n") as f:
            for op in ("get_payload", "set_payload", "set_payload_signaling"):
                nm = opname("f16", op)
                for a in range(65536):
                    f.write("%s - %x -> %x -- audit:gate-payload-f16\n"
                            % (nm, a, ref_payload("f16", op, a)))
                    n += 1
            s = spec("f16")
            for k in range(s["pmax"] + 1):
                enc = int_pattern("f16", k)
                r = ref_set("f16", enc, False)
                f.write("msf16_is_signaling - %x -> 0 -- audit:gate-payload-f16\n" % r)
                n += 1
                if k >= 1:
                    r = ref_set("f16", enc, True)
                    f.write("msf16_is_signaling - %x -> 1 -- audit:gate-payload-f16\n" % r)
                    n += 1
        # my own round-trip law, asserted here
        for k in range(spec("f16")["pmax"] + 1):
            enc = int_pattern("f16", k)
            assert ref_get("f16", ref_set("f16", enc, False)) == enc, k
            if k >= 1:
                assert ref_get("f16", ref_set("f16", enc, True)) == enc, k
        print("wrote %s (%d cases); round-trips hold 512+511" % (out, n))
    elif mode == "gate-minmax-sample":
        # 8 boundary firsts x every-16th second x 8 ops, f16
        out = sys.argv[2]
        s = spec("f16")
        b = s["bias"]
        emax = s["emax"]
        mk = lambda sg, e, f: (sg << 15) | (e << 10) | f  # noqa
        qn = lambda sg, p: mk(sg, emax, s["qbit"] | p)  # noqa
        sn = lambda sg, p: mk(sg, emax, p)  # noqa
        firsts = [s["sign"] | s["inf"], mk(1, b, 0), s["sign"], 0,
                  mk(0, b, 0), s["inf"], qn(0, 0x155 & s["pmax"]),
                  sn(1, 0x155 & s["pmax"] or 1)]
        ops = ("minimum", "maximum", "minimum_number", "maximum_number",
               "minimum_magnitude", "maximum_magnitude",
               "minimum_magnitude_number", "maximum_magnitude_number")
        n = 0
        with open(out, "w", newline="\n") as f:
            for a in firsts:
                for x in range(0, 65536, 16):
                    for op in ops:
                        r, fl = ref_minmax("f16", op, a, x)
                        f.write("%s - %x %x -> %x %02x audit:gate-minmax-sample\n"
                                % (opname("f16", op), a, x, r, fl))
                        n += 1
        print("wrote %s (%d cases)" % (out, n))
    elif mode == "gate-seeded":
        out, narg = sys.argv[2], int(sys.argv[3])
        rng = random.Random(20261027)
        n = 0
        with open(out, "w", newline="\n") as f:
            for fmt in ("f32", "f64"):
                s = spec(fmt)
                emax = s["emax"]
                for _ in range(narg):
                    a = rng.randrange(1 << s["bits"])
                    b = rng.randrange(1 << s["bits"])
                    for op in ("minimum", "maximum", "minimum_number",
                               "maximum_number", "minimum_magnitude",
                               "maximum_magnitude",
                               "minimum_magnitude_number",
                               "maximum_magnitude_number"):
                        r, fl = ref_minmax(fmt, op, a, b)
                        f.write("%s - %x %x -> %x %02x audit:gate-seeded\n"
                                % (opname(fmt, op), a, b, r, fl))
                        n += 1
                for _ in range(narg):
                    a = rng.randrange(1 << s["bits"])
                    for op in ("get_payload", "set_payload",
                               "set_payload_signaling"):
                        f.write("%s - %x -> %x -- audit:gate-seeded\n"
                                % (opname(fmt, op), a, ref_payload(fmt, op, a)))
                        n += 1
        print("wrote %s (%d cases)" % (out, n))
    elif mode == "cell-coverage":
        # enumerate (class,class,sign,sign,magorder) cells in committed vectors
        vec = sys.argv[2]
        cells = {}
        with open(vec) as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                t = line.split()
                op, a, b = t[0], int(t[2], 16), int(t[3], 16)
                fmt = "f" + op[3:5]
                ca, sa, _ = decode(fmt, a)
                cb, sb, _ = decode(fmt, b)
                va, vb = exact_value(fmt, a), exact_value(fmt, b)
                if va is None or vb is None:
                    mo = "nan"
                else:
                    mo = "lt" if abs(va) < abs(vb) else ("gt" if abs(va) > abs(vb) else "eq")
                key = (op, ca, cb, sa, sb, mo)
                cells[key] = cells.get(key, 0) + 1
        print("%s: %d distinct cells" % (vec, len(cells)))
        # every ordered class pair present for each op?
        classes = ("zero", "sub", "normal", "inf", "qnan", "snan")
        ops = sorted(set(k[0] for k in cells))
        missing = 0
        for op in ops:
            for ca in classes:
                for cb in classes:
                    if not any(k[0] == op and k[1] == ca and k[2] == cb for k in cells):
                        print("MISSING", op, ca, cb)
                        missing += 1
        print("missing class-pairs: %d" % missing)
    else:
        print("unknown mode", mode)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
