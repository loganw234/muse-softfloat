"""Probe 6: exhaustive unary f16->f16 (all 65536 encodings) from the reference."""
import sys
sys.path.insert(0, "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16")
from ref_f16 import *

SC = "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
PROV = "verifier-w2f16:exhaustive-ref"


def dump(name, rm, fn, has_flags=True):
    op = name.split("@")[0]
    with open("%s/exh-%s.vec" % (SC, name), "w", newline="\n") as f:
        f.write("# exhaustive %s from independent reference\n" % name)
        f.write("# compare=exact\n")
        for u in range(65536):
            if "from_f16" in op:
                r, f_ = op_from_f16(u, rm)
            elif "sqrt" in op:
                r, f_ = op_sqrt(u, rm)
            elif op.endswith("exact"):
                r, f_ = op_rint(u, "exact", rm)
            elif "round_to_integral" in op:
                mode = op.split("round_to_integral_")[1]
                r, f_ = op_rint(u, mode)
            elif "next_up" in op:
                r, f_ = op_next_up(u)
            elif "next_down" in op:
                r, f_ = op_next_down(u)
            f.write("msf16_%s %s %04x -> %x %02x %s\n" % (op, rm, u, r, f_, PROV))


jobs = []
for rm in ("te", "tz", "tp", "tn", "ta"):
    jobs.append(("sqrt", rm))
    jobs.append(("from_f16", rm))
    for m in ("ties_to_even", "ties_to_away", "toward_zero",
              "toward_positive", "toward_negative"):
        jobs.append(("round_to_integral_%s" % m, "-"))
jobs.append(("round_to_integral_exact", "te"))
jobs.append(("next_up", "-"))
jobs.append(("next_down", "-"))
seen = set()
for op, rm in jobs:
    tag = "%s@%s" % (op, rm)
    if tag in seen:
        continue
    seen.add(tag)
    dump(tag, rm, None)
print("wrote", len(seen), "files")
