import re
import sys
sys.path.insert(0, "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16")
from ref_f16 import op_rem, op_total_order, op_total_order_mag

SC = "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
# 1. ref remainder vs Berkeley L1 expectations
pat = re.compile(r'msf16_remainder - ([0-9a-f]+) ([0-9a-f]+) -> ([0-9a-f]+) ([0-9a-f]+)')
n = bad = 0
badex = []
with open(SC + "/berk1/f16_rem-l1.vec") as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        m = pat.search(line)
        a, b, wv, wf = int(m.group(1), 16), int(m.group(2), 16), int(m.group(3), 16), int(m.group(4), 16)
        n += 1
        r, fl = op_rem(a, b)
        if r != wv or fl != wf:
            bad += 1
            if len(badex) < 5:
                badex.append((line.strip()[-80:], hex(r), hex(fl)))
print("rem: ref-vs-Berkeley %d cases, mismatches=%d" % (n, bad))
for b in badex:
    print("   ", b)
# 2. ref totalOrder vs committed directed expectations
pat2 = re.compile(r'(msf16_total_order(?:_mag)?) - ([0-9a-f]+) ([0-9a-f]+) -> ([01]) --')
n2 = bad2 = 0
badex2 = []
with open("C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16/tests/vectors/compare-f16.vec") as f:
    for line in f:
        m = pat2.search(line)
        if not m:
            continue
        op, a, b, w = m.group(1), int(m.group(2), 16), int(m.group(3), 16), int(m.group(4))
        n2 += 1
        r, _ = op_total_order(a, b) if op == "msf16_total_order" else op_total_order_mag(a, b)
        if r != w:
            bad2 += 1
            if len(badex2) < 5:
                badex2.append(line.strip())
print("totalOrder: ref-vs-committed %d cases, mismatches=%d" % (n2, bad2))
for b in badex2:
    print("   ", b)
