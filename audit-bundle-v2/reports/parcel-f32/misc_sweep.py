"""Seeded misc-op sweep for parcel-f32 using the committed references."""
import importlib.util, random, sys
from pathlib import Path

sys.path.insert(0, "C:\\Users\\logan\\source\\repos\\Muse-Softfloat\\worktrees\\w1-f32\\tests")
import gen_vectors_f32 as g

OUT = sys.argv[1]
N = int(sys.argv[2])
SEED = int(sys.argv[3])
rng = random.Random(SEED)
prov = "exact-py-f32:misc-sweep-%d" % SEED
out = []

def r32():
    return g.random_bits(rng, "f32")

def r64():
    return g.random_bits(rng, "f64")

named = [("ties_to_even", "te"), ("ties_to_away", "ta"),
         ("toward_zero", "tz"), ("toward_positive", "tp"),
         ("toward_negative", "tn")]

templates = []
for sfx, mode in named:
    templates.append(("rint", sfx, mode))
templates.append(("rint_exact",))
templates += [("next_up",), ("next_down",), ("log_b",), ("remainder",),
              ("scale_b",), ("total_order",), ("total_order_mag",)]
for tok in g.INT_KINDS:
    templates.append(("from_int", tok))
for tok in g.INT_KINDS:
    for suffix, mode, exact_form in g.INT_MODES:
        templates.append(("to_int", tok, suffix, mode, exact_form))
for suffix, relset, signaling in g.CMP_PREDS:
    templates.append(("cmp", suffix, relset, signaling, "f32"))
    templates.append(("cmp", suffix, relset, signaling, "f64"))

for i in range(N):
    tpl = templates[i % len(templates)]
    k = tpl[0]
    if k == "rint":
        a = r32()
        r, f = g.ref_rint(a, tpl[2], 0, "te")
        out.append(g.vline("msf32_round_to_integral_%s" % tpl[1], "-", [a], r, f, prov))
    elif k == "rint_exact":
        a, rm = r32(), rng.choice(g.RMS4)
        r, f = g.ref_rint(a, "te", 1, rm)
        out.append(g.vline("msf32_round_to_integral_exact", rm, [a], r, f, prov))
    elif k in ("next_up", "next_down"):
        a = r32()
        r, f = g.ref_next(a, 1 if k == "next_up" else 0)
        out.append(g.vline("msf32_%s" % k, "-", [a], r, f, prov))
    elif k == "log_b":
        a = r32()
        r, f = g.ref_logb(a)
        out.append(g.vline("msf32_log_b", "-", [a], r, f, prov))
    elif k == "remainder":
        # bias toward same-binade pairs for tie/quotient-parity coverage
        a = r32()
        b = r32() if rng.random() < 0.5 else (a & 0x007fffff) | (r32() & 0xff800000)
        r, f = g.ref_remainder(a, b)
        out.append(g.vline("msf32_remainder", "-", [a, b], r, f, prov))
    elif k == "scale_b":
        a, nb, rm = r32(), r64(), rng.choice(g.RMS4)
        r, f = g.ref_scaleb(a, nb, rm)
        out.append(g.vline("msf32_scale_b", rm, [a, nb], r, f, prov))
    elif k in ("total_order", "total_order_mag"):
        a, b = r32(), r32()
        r, _ = g.ref_total_order(a, b, 1 if k.endswith("mag") else 0)
        out.append(g.vline("msf32_%s" % k, "-", [a, b], r, None, prov))
    elif k == "from_int":
        tok = tpl[1]
        is_signed, width = g.INT_KINDS[tok]
        lo = -(1 << (width - 1)) if is_signed else 0
        hi = (1 << (width - 1)) - 1 if is_signed else (1 << width) - 1
        v = rng.randint(lo, hi) if rng.random() < 0.7 else rng.choice([lo, hi, 0, -1 if is_signed else 1])
        rm = rng.choice(g.RMS4)
        r, f = g.ref_from_int(v, rm)
        out.append(g.vline("msf32_from_%s" % tok, rm, [v & ((1 << width) - 1)], r, f, prov))
    elif k == "to_int":
        _, tok, suffix, mode, exact_form = tpl
        a = r32()
        r, f = g.ref_to_int(a, tok, mode, exact_form)
        out.append(g.vline("msf32_to_%s_%s" % (tok, suffix), "-", [a], r, f, prov))
    else:
        _, suffix, relset, signaling, bfmt = tpl
        a = r32()
        b = r64() if bfmt == "f64" else r32()
        r, f = g.ref_compare("f32", a, bfmt, b, relset, signaling)
        name = "msf32_compare_%s%s" % (suffix, "_f64" if bfmt == "f64" else "")
        out.append(g.vline(name, "-", [a, b], r, f, prov))

g.write_file(OUT, out)
