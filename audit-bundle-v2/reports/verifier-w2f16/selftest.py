import sys
sys.path.insert(0, "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16")
from ref_f16 import *

fails = []


def ck(name, got, want):
    if got != want:
        fails.append((name, got, want))


ck("add 1+1", op_add(0x3C00, 0x3C00, "te"), (0x4000, 0))
ck("add 0+1", op_add(0x0000, 0x3C00, "te"), (0x3C00, 0))
ck("sub 0-inf", op_sub(0x0000, 0x7C00, "te"), (0xFC00, 0))
ck("sub 0-ninf", op_sub(0x0000, 0xFC00, "te"), (0x7C00, 0))
ck("div 1/1", op_div(0x3C00, 0x3C00, "te"), (0x3C00, 0))
ck("div 1/0", op_div(0x3C00, 0x0000, "te"), (0x7C00, 0x02))
ck("div 0/0", op_div(0x0000, 0x0000, "te"), (0x7E00, 0x01))
ck("mul submin*submin", op_mul(0x0001, 0x0001, "te"), (0x0000, 0x18))
ck("mul 1*1", op_mul(0x3C00, 0x3C00, "te"), (0x3C00, 0))
ck("sqrt 4", op_sqrt(0x4400, "te"), (0x4000, 0))
ck("sqrt -0", op_sqrt(0x8000, "te"), (0x8000, 0))
ck("sqrt -1", op_sqrt(0xBC00, "te"), (0x7E00, 0x01))
ck("sqrt 2", op_sqrt(0x4000, "te"), (0x3DA8, 0x10))
ck("rem 1/-1", op_rem(0x3C00, 0xBC00), (0x0000, 0))
ck("rem 5.5/2", op_rem(0x45C0, 0x4000), (0xBC00, 0))
ck("rint te 0.5", op_rint(0x3800, "ties_to_even"), (0x0000, 0))
ck("rint ta 0.5", op_rint(0x3800, "ties_to_away"), (0x3C00, 0))
ck("rint exact 0.5", op_rint(0x3800, "exact"), (0x0000, 0x10))
ck("nextup 0", op_next_up(0x0000), (0x0001, 0))
ck("nextdown 0", op_next_down(0x0000), (0x8001, 0))
ck("nextup max", op_next_up(0x7BFF), (0x7C00, 0))
ck("nextdown max", op_next_down(0x7BFF), (0x7BFE, 0))
ck("from32 1.5", op_from_f32(0x3FC00000, "te"), (0x3E00, 0))
ck("from32 snan1", op_from_f32(0x7F800001, "te"), (0x7E00, 0x01))
ck("from32 qnan", op_from_f32(0xFFC12345, "te"), (0xFE09, 0))
ck("scaleB 1,2.5", op_scale_b(0x3C00, 0x4004000000000000, "te"), (0x4400, 0))
ck("scaleB 1,-2.5", op_scale_b(0x3C00, 0xC004000000000000, "te"), (0x3400, 0))
ck("logB 1", op_log_b(0x3C00), (0x0000000000000000, 0))
ck("logB submin", op_log_b(0x0001), (0xC038000000000000, 0))
ck("logB 0", op_log_b(0x0000), (0xFFF0000000000000, 0x02))
ck("to 1vs1", op_total_order(0x3C00, 0x3C00), (1, None))
ck("to -nan", op_total_order(0xFFFF, 0x7E00), (1, None))
ck("cmp qeq nan", op_compare("quiet_equal", 0x7E00, 0x3C00), (0, 0))
ck("cmp seq nan", op_compare("signaling_equal", 0x7E00, 0x3C00), (0, 0x01))
ck("add z z tn", op_add(0x0000, 0x0000, "tn"), (0x0000, 0))
ck("add pmz tn", op_add(0x0000, 0x8000, "tn"), (0x8000, 0))
ck("add canc tn", op_add(0x3C00, 0xBC00, "tn"), (0x8000, 0))
ck("add canc te", op_add(0x3C00, 0xBC00, "te"), (0x0000, 0))
ck("div te tiny", op_div(0x0001, 0x4000, "te"), (0x0000, 0x18))
ck("div exact submin", op_div(0x0002, 0x4000, "te"), (0x0001, 0))

print("fails:", len(fails))
for n, g, w in fails:
    print("  MISMATCH", n, "got", hex(g[0]), hex(g[1]) if g[1] is not None else None,
          "want", hex(w[0]), hex(w[1]) if w[1] is not None else None)
