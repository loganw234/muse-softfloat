import sys
sys.path.insert(0, "C:\\Users\\logan\\source\\repos\\Muse-Softfloat\\scratch\\parcel-f32")
import patched_gen as g
from pathlib import Path

def isnan32(b):
    return ((b >> 23) & 0xff) == 0xff and (b & 0x7fffff) != 0

for fn_name, ref in [("mul", g.ref_mul), ("div", g.ref_div)]:
    for rm in ["te", "tz", "tp", "tn", "ta"]:
        p = Path("worktrees/w1-f32/build/w1/f32_%s-%s-l1.vec" % (fn_name, rm))
        bad = 0; n = 0; examples = []
        for line in p.read_text().splitlines():
            if not line or line.startswith("#"):
                continue
            t = line.split()
            a, b = int(t[2], 16), int(t[3], 16)
            want_r, want_f = int(t[5], 16), int(t[6], 16)
            got_r, got_f = ref("f32", a, "f32", b, rm)
            ok = (got_f == want_f) and (got_r == want_r or (isnan32(want_r) and isnan32(got_r)))
            n += 1
            if not ok:
                bad += 1
                if len(examples) < 3:
                    examples.append((line, got_r, got_f))
        print(fn_name, rm, "n=%d bad=%d" % (n, bad))
        for e in examples:
            print("   ", e)
