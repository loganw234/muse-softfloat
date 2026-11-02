import re
import sys
sys.path.insert(0, "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16")
from ref_f16 import op_rem, dec

SC = "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
pat = re.compile(r'msf16_remainder - ([0-9a-f]+) ([0-9a-f]+) -> ([0-9a-f]+) ([0-9a-f]+)')
n = bad = 0
nondefault = []
with open(SC + "/berk1/f16_rem-l1.vec") as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        m = pat.search(line)
        a, b = int(m.group(1), 16), int(m.group(2), 16)
        wv, wf = int(m.group(3), 16), int(m.group(4), 16)
        n += 1
        r, fl = op_rem(a, b)
        if r != wv or fl != wf:
            bad += 1
            da, db = dec(a), dec(b)
            ok = (fl == wf == 0x01 and (wv & 0x7FFF) == 0x7E00 and (r & 0x7FFF) == 0x7E00)
            if not ok and len(nondefault) < 8:
                nondefault.append((line.strip()[-90:], hex(r), hex(fl),
                                   da["cls"], db["cls"]))
print("rem mismatches:", bad, "of", n, "; non-default-NaN-invalid:", len(nondefault))
for x in nondefault:
    print("   ", x)
