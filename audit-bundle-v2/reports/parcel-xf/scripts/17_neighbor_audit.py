"""Independent audit of gen_vectors_xf expectations: for sampled
sweep lines, recompute the exact result E from the operands with
Fractions (sqrt handled by squared boundaries, never by the
generator's packer), then verify the expected bits are the correct
rounding of E by the neighbor/midpoint definition and that the
inexact flag matches E != delivered. This shares no code path with
pack_mag (the generator's rounding implementation) except Dec.
"""
import importlib.util
import pathlib
import sys
from fractions import Fraction

ROOT = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
WT = ROOT / "worktrees" / "w2-xf"
spec = importlib.util.spec_from_file_location(
    "gen_vectors_xf", WT / "tests" / "gen_vectors_xf.py")
gx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gx)
Dec, fmt_consts = gx.Dec, gx.fmt_consts


def neighbors(fmt, bits):
    """(below_value, above_value) as Fractions around a finite bits."""
    c = fmt_consts(fmt)
    sign = 1 if bits & c["signbit"] else 0
    mag = bits & ~c["signbit"]
    def val(b):
        d = Dec(fmt, b)
        return None if d.cls in ("inf", "qnan", "snan") else d.value()
    if sign == 0:
        below = val(bits - 1) if mag > 0 else val(c["signbit"] | 1)
        above = val(bits + 1)
    else:
        below = val(bits + 1)
        above = val(bits - 1) if mag > 0 else val(1)
    return below, above


def check_rounding(dest, rm, E, bits):
    d = Dec(dest, bits)
    assert d.cls in ("finite", "zero")
    g = d.value()
    if E == g:
        return True
    below, above = neighbors(dest, bits)
    if below is None or above is None:
        return None  # overflow boundary: not audited here
    if rm == "te":
        lo_m, hi_m = (below + g) / 2, (g + above) / 2
        if lo_m < E < hi_m:
            return True
        if E == lo_m or E == hi_m:
            return (bits & 1) == 0  # ties to even significand
        return False
    if rm == "tz":
        return (g <= E < above) if E >= 0 else (below < E <= g)
    if rm == "tp":
        return below < E <= g
    if rm == "tn":
        return g <= E < above
    raise AssertionError(rm)


def exact_value(name, argbits):
    """Exact Fraction result, or ('sqrt', input value), or None to skip."""
    parts = name.split("_")
    if parts[1] == "sqrt":
        d = Dec("f16", argbits[0])
        if d.cls != "finite" or d.sign:
            return None
        return ("sqrt", d.value())
    if parts[1] == "from":
        d = Dec("f16", argbits[0])
        return d.value() if d.cls in ("finite", "zero") else None
    if parts[1] == "fma":
        fmts = parts[2:5]
        ds = [Dec(f, b) for f, b in zip(fmts, argbits)]
        if any(d.cls not in ("finite", "zero") for d in ds):
            return None
        return ds[0].value() * ds[1].value() + ds[2].value()
    if parts[1] in ("add", "sub", "mul", "div"):
        fmts = parts[2:4]
        da, db = Dec(fmts[0], argbits[0]), Dec(fmts[1], argbits[1])
        if da.cls not in ("finite", "zero") or db.cls not in ("finite", "zero"):
            return None
        va, vb = da.value(), db.value()
        if parts[1] == "add":
            return va + vb
        if parts[1] == "sub":
            return va - vb
        if parts[1] == "mul":
            return va * vb
        return None if vb == 0 else va / vb
    return None  # comparisons not audited here


def audit_file(path, step):
    checked = skipped = bad = 0
    lines = pathlib.Path(path).read_text().splitlines()
    for ln, l in enumerate(lines):
        if not l or l.startswith("#") or ln % step != 0:
            continue
        tok = l.split()
        name, rm = tok[0], tok[1]
        if "_compare_" in name:
            skipped += 1
            continue
        k = tok.index("->")
        argbits = [int(x, 16) for x in tok[2:k]]
        bits, flags = int(tok[k + 1], 16), int(tok[k + 2], 16)
        dest = "f" + name[3:5]
        E = exact_value(name, argbits)
        if E is None:
            skipped += 1
            continue
        d = Dec(dest, bits)
        if d.cls not in ("finite", "zero"):
            skipped += 1
            continue
        if isinstance(E, tuple):  # sqrt: compare squares to boundaries
            v = E[1]
            g = d.value()
            if g * g == v:
                ok = True
                inexact = False
            else:
                below, above = neighbors(dest, bits)
                if below is None or above is None:
                    skipped += 1
                    continue
                # E = sqrt(v); boundary comparisons via squares
                class SqrtVal:
                    pass
                # emulate check_rounding with squared midpoints
                lo_m2 = ((below + g) / 2) ** 2
                hi_m2 = ((g + above) / 2) ** 2
                if rm == "te":
                    ok = (lo_m2 < v < hi_m2) or \
                         ((v == lo_m2 or v == hi_m2) and (bits & 1) == 0)
                elif rm == "tz" or rm == "tn":  # sqrt result >= 0
                    ok = g * g <= v < above * above
                else:  # tp
                    ok = below * below < v <= g * g
                inexact = True
            if not ok or bool(flags & gx.FLAG_INX) != inexact:
                bad += 1
                print("BAD sqrt %s | %s" % (path, l))
            checked += 1
            continue
        ok = check_rounding(dest, rm, E, bits)
        if ok is None:
            skipped += 1
            continue
        inexact = (E != d.value())
        if not ok or bool(flags & gx.FLAG_INX) != inexact:
            bad += 1
            print("BAD %s | %s (ok=%s inexact=%s flags=%02x)"
                  % (path, l, ok, inexact, flags))
        checked += 1
    print("%s: audited %d, skipped %d, bad %d" % (path, checked, skipped, bad))
    return checked, bad


def main():
    total_checked = total_bad = 0
    for f in sys.argv[1:]:
        c, b = audit_file(f, 37)
        total_checked += c
        total_bad += b
    print("neighbor audit total: %d checked, %d bad" % (total_checked, total_bad))
    return 1 if total_bad else 0


if __name__ == "__main__":
    sys.exit(main())
