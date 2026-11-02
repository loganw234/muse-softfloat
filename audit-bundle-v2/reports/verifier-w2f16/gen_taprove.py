import sys
sys.path.insert(0, "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16")
from ref_f16 import *

SC = "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
lines = []
# sqrt(2) across modes: discriminates ta/tp vs te/tz/tn
for rm in ("te", "tz", "tp", "tn", "ta"):
    r, fl = op_sqrt(0x4000, rm)
    lines.append("msf16_sqrt %s 4000 -> %x %02x ta-probe" % (rm, r, fl))
# mul tiny across modes
for rm in ("te", "tz", "tp", "tn", "ta"):
    r, fl = op_mul(0x0001, 0x0001, rm)
    lines.append("msf16_mul %s 0001 0001 -> %x %02x ta-probe" % (rm, r, fl))
    r, fl = op_mul(0x3400, 0x0001, rm)
    lines.append("msf16_mul %s 3400 0001 -> %x %02x ta-probe" % (rm, r, fl))
# from_f32 tiny across modes
for rm in ("te", "tz", "tp", "tn", "ta"):
    r, fl = op_from_f32(0x00000001, rm)
    lines.append("msf16_from_f32 %s 00000001 -> %x %02x ta-probe" % (rm, r, fl))
# add tiny-sum across modes: submin + submin = 2^-23 exact (control, exact)
for rm in ("te", "tz", "tp", "tn", "ta"):
    r, fl = op_add(0x0001, 0x0001, rm)
    lines.append("msf16_add %s 0001 0001 -> %x %02x ta-probe" % (rm, r, fl))
# add inexact normal across modes (control: L1 says ta works)
for rm in ("te", "tz", "tp", "tn", "ta"):
    r, fl = op_add(0x3C01, 0x3BFF, rm)
    lines.append("msf16_add %s 3c01 3bff -> %x %02x ta-probe" % (rm, r, fl))
# mul inexact normal across modes (control)
for rm in ("te", "tz", "tp", "tn", "ta"):
    r, fl = op_mul(0x3D00, 0x3D00, rm)
    lines.append("msf16_mul %s 3d00 3d00 -> %x %02x ta-probe" % (rm, r, fl))
with open(SC + "/ta-probe.vec", "w", newline="\n") as f:
    f.write("# ta-probe\n# compare=exact\n" + "\n".join(lines) + "\n")
print("wrote", len(lines))
