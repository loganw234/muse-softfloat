"""Probe 5: directed edge cases from the independent reference."""
import sys
sys.path.insert(0, "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16")
from ref_f16 import *

SC = "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
PROV = "verifier-w2f16:independent-ref-edge"

exact_lines = []
nc_lines = []


def E(op, rm, ops, res, fl, width=4):
    w = width * 4
    opss = " ".join("%0*x" % (w if i == 0 and width == 4 and False else
                              (16 if width == 16 else 4), o)
                    for i, o in enumerate(ops))
    exact_lines.append("%s %s %s -> %x %02x %s" % (op, rm, opss, res, fl, PROV))


def E64(op, rm, a16, b64, res, fl):
    exact_lines.append("%s %s %04x %016x -> %x %02x %s" % (op, rm, a16, b64, res, fl, PROV))


def E6(op, rm, a16, res64, fl):
    exact_lines.append("%s %s %04x -> %016x %02x %s" % (op, rm, a16, res64, fl, PROV))


def NC(op, rm, ops, res, fl):
    opss = " ".join("%04x" % o for o in ops)
    nc_lines.append("%s %s %s -> %x %02x %s" % (op, rm, opss, res, fl, PROV))


SUBMIN = 0x0001
# 1. tininess boundary at smallest subnormal
for rm in ("te", "tz", "tp", "tn", "ta"):
    E("msf16_mul", rm, (SUBMIN, SUBMIN), *op_mul(SUBMIN, SUBMIN, rm))
    E("msf16_mul", rm, (0x3400, SUBMIN), *op_mul(0x3400, SUBMIN, rm))
    E("msf16_div", rm, (SUBMIN, 0x4000), *op_div(SUBMIN, 0x4000, rm))
    E("msf16_div", rm, (0x0002, 0x4000), *op_div(0x0002, 0x4000, rm))
    E("msf16_add", rm, (SUBMIN, 0x8001), *op_add(SUBMIN, 0x8001, rm))
    E("msf16_sqrt", rm, (SUBMIN,), *op_sqrt(SUBMIN, rm))
    E("msf16_sqrt", rm, (0x0002,), *op_sqrt(0x0002, rm))
    E("msf16_from_f32", rm, (0x00000001,), *op_from_f32(0x00000001, rm))
    E("msf16_from_f64", rm, (0x0000000000000001,), *op_from_f64(0x1, rm))

# 2. NaN payload narrow incl truncate-to-default (exact expectations)
for rm in ("te", "tz", "tp", "tn"):
    E("msf16_from_f32", rm, (0x7FC00000,), *op_from_f32(0x7FC00000, rm))
    E("msf16_from_f32", rm, (0x7F800001,), *op_from_f32(0x7F800001, rm))
    E("msf16_from_f32", rm, (0xFFC12345,), *op_from_f32(0xFFC12345, rm))
    E("msf16_from_f32", rm, (0xFFBFFFFF,), *op_from_f32(0xFFBFFFFF, rm))
    E("msf16_from_f32", rm, (0x7FFFFFFF,), *op_from_f32(0x7FFFFFFF, rm))
    E("msf16_from_f64", rm, (0x7FF0000000000001,), *op_from_f64(0x7FF0000000000001, rm))
    E("msf16_from_f64", rm, (0xFFF8000000000000,), *op_from_f64(0xFFF8000000000000, rm))
    E("msf16_from_f64", rm, (0x7FF7FFFFFFFFFFFF,), *op_from_f64(0x7FF7FFFFFFFFFFFF, rm))
    E("msf16_from_f16", rm, (0x7C01,), *op_from_f16(0x7C01, rm))
    E("msf16_from_f16", rm, (0xFE09,), *op_from_f16(0xFE09, rm))
# widening-direction NaN: f16->f16 identity incl sNaN quieten
E("msf16_from_f16", "te", (0xFC01,), *op_from_f16(0xFC01, "te"))

# 3. signed zeros
for rm in ("te", "tn"):
    E("msf16_add", rm, (0x0000, 0x0000), *op_add(0, 0, rm))
    E("msf16_add", rm, (0x0000, 0x8000), *op_add(0, 0x8000, rm))
    E("msf16_add", rm, (0x8000, 0x8000), *op_add(0x8000, 0x8000, rm))
    E("msf16_sub", rm, (0x0000, 0x0000), *op_sub(0, 0, rm))
    E("msf16_sub", rm, (0x0000, 0x8000), *op_sub(0, 0x8000, rm))
    E("msf16_mul", rm, (0x8000, 0x3C00), *op_mul(0x8000, 0x3C00, rm))
    E("msf16_div", rm, (0x8000, 0x3C00), *op_div(0x8000, 0x3C00, rm))
    E("msf16_div", rm, (0x0000, 0x8000), *op_div(0, 0x8000, rm))
    E("msf16_div", rm, (0x3C00, 0x8000), *op_div(0x3C00, 0x8000, rm))
    E("msf16_sqrt", rm, (0x8000,), *op_sqrt(0x8000, rm))
    E("msf16_round_to_integral_ties_to_even", "-", (0x8000,), *op_rint(0x8000, "ties_to_even"))
    E("msf16_from_f32", rm, (0x80000000,), *op_from_f32(0x80000000, rm))
    E64("msf16_scale_b", rm, 0x8000, 0x4000000000000000, *op_scale_b(0x8000, 0x4000000000000000, rm))

# 4. remainder ties (quotient exactly half, even/odd n) + signs
E("msf16_remainder", "-", (0x3C00, 0x4000), *op_rem(0x3C00, 0x4000))
E("msf16_remainder", "-", (0x4400, 0x4000), *op_rem(0x4400, 0x4000))
E("msf16_remainder", "-", (0x4200, 0x4000), *op_rem(0x4200, 0x4000))
E("msf16_remainder", "-", (0x4600, 0x4000), *op_rem(0x4600, 0x4000))
E("msf16_remainder", "-", (0xBC00, 0x4000), *op_rem(0xBC00, 0x4000))
E("msf16_remainder", "-", (0xC400, 0x4000), *op_rem(0xC400, 0x4000))
E("msf16_remainder", "-", (0x3C00, 0xBC00), *op_rem(0x3C00, 0xBC00))
E("msf16_remainder", "-", (0x3C00, 0x0000), *op_rem(0x3C00, 0x0000))
E("msf16_remainder", "-", (0x7C00, 0x3C00), *op_rem(0x7C00, 0x3C00))
E("msf16_remainder", "-", (0x3C00, 0x7C00), *op_rem(0x3C00, 0x7C00))
E("msf16_remainder", "-", (0x0001, 0x3C00), *op_rem(0x0001, 0x3C00))

# 5. totalOrder incl negative NaNs payload-descending + mag
def T(op, a, b):
    bit, _ = op_total_order(a, b) if op == "msf16_total_order" else op_total_order_mag(a, b)
    exact_lines.append("%s - %04x %04x -> %x -- %s" % (op, a, b, bit, PROV))


T("msf16_total_order", 0xFFFF, 0xFE00)
T("msf16_total_order", 0xFE00, 0xFFFF)
T("msf16_total_order", 0xFC01, 0xFC00)
T("msf16_total_order", 0xFC00, 0xFC01)
T("msf16_total_order", 0x8001, 0x8001)
T("msf16_total_order", 0x8000, 0x0000)
T("msf16_total_order", 0x0000, 0x8000)
T("msf16_total_order", 0x7E00, 0x7E01)
T("msf16_total_order", 0xFC00, 0x7C00)
T("msf16_total_order", 0x7C00, 0xFC00)
T("msf16_total_order_mag", 0xBC00, 0x3C00)
T("msf16_total_order_mag", 0xFC01, 0x7C01)

# 6. scaleB non-integral N (truncate toward zero) + huge N
E64("msf16_scale_b", "te", 0x3C00, 0x4004000000000000, *op_scale_b(0x3C00, 0x4004000000000000, "te"))
E64("msf16_scale_b", "te", 0x3C00, 0xC004000000000000, *op_scale_b(0x3C00, 0xC004000000000000, "te"))
E64("msf16_scale_b", "te", 0x3C00, 0x3FF0000000000000, *op_scale_b(0x3C00, 0x3FF0000000000000, "te"))
E64("msf16_scale_b", "te", 0x3C00, 0xBFF0000000000000, *op_scale_b(0x3C00, 0xBFF0000000000000, "te"))
E64("msf16_scale_b", "te", 0x3C00, 0x4330000000000000, *op_scale_b(0x3C00, 0x4330000000000000, "te"))
E64("msf16_scale_b", "tn", 0x3C00, 0x4330000000000000, *op_scale_b(0x3C00, 0x4330000000000000, "tn"))
E64("msf16_scale_b", "te", 0x3C00, 0xC330000000000000, *op_scale_b(0x3C00, 0xC330000000000000, "te"))
E64("msf16_scale_b", "tp", 0x3C00, 0xC330000000000000, *op_scale_b(0x3C00, 0xC330000000000000, "tp"))
E64("msf16_scale_b", "te", 0x3C00, 0x0000000000000000, *op_scale_b(0x3C00, 0, "te"))
E64("msf16_scale_b", "te", 0x0000, 0x40C3880000000000, *op_scale_b(0, 0x40C3880000000000, "te"))
E64("msf16_scale_b", "te", 0x7C00, 0x40C3880000000000, *op_scale_b(0x7C00, 0x40C3880000000000, "te"))

# 7. logB incl subnormal leading-zero count
for a in (0x0001, 0x03FF, 0x0400, 0x7BFF, 0x3C00, 0xBC01, 0x8000, 0x0000, 0x7C00, 0xFC00):
    r, fl = op_log_b(a)
    E6("msf16_log_b", "-", a, r, fl)

# 8. arithmetic NaN propagation (nan-class: quiet result + invalid only for sNaN)
for a, b in ((0x7E00, 0x3C00), (0x3C00, 0x7E00), (0x7C01, 0x3C00), (0x3C00, 0xFC01),
              (0xFE00, 0xFE00), (0x7E00, 0x7E00)):
    for op, fn in (("msf16_add", op_add), ("msf16_sub", op_sub),
                   ("msf16_mul", op_mul), ("msf16_div", op_div)):
        r, fl = fn(a, b, "te")
        rr = r if not is_nan_d(r) else (0x7E00 if (r >> 15) == 0 else 0xFE00)
        NC(op, "te", (a, b), rr, fl)
    r, fl = op_sqrt(a, "te")
    rr = r if not is_nan_d(r) else (0x7E00 if (r >> 15) == 0 else 0xFE00)
    NC("msf16_sqrt", "te", (a,), rr, fl)
    r, fl = op_rem(a, b)
    rr = r if not is_nan_d(r) else (0x7E00 if (r >> 15) == 0 else 0xFE00)
    NC("msf16_remainder", "-", (a, b), rr, fl)

with open(SC + "/edge-exact.vec", "w", newline="\n") as f:
    f.write("# generated by verifier-w2f16 gen_edge.py (independent reference)\n")
    f.write("# compare=exact\n")
    f.write("\n".join(exact_lines) + "\n")
with open(SC + "/edge-nanclass.vec", "w", newline="\n") as f:
    f.write("# generated by verifier-w2f16 gen_edge.py (independent reference)\n")
    f.write("# compare=nan-class\n")
    f.write("\n".join(nc_lines) + "\n")
print("wrote", len(exact_lines), "exact +", len(nc_lines), "nanclass")
