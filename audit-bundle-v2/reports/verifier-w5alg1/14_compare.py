"""14_compare.py - kernel sweep vs my decider for f32/f64 lists."""
import importlib.util
import sys
import time

t0 = time.time()
_spec = importlib.util.spec_from_file_location(
    "mydec", "scratch/verifier-w5alg1/10_mydecider.py")
mydec = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mydec)

fmt = sys.argv[1]
total = mism = 0
shown = 0
cls_tot = {}
cls_mis = {}


def cls_of(fmt, x):
    c = mydec.classify(fmt, x)[0]
    return c


with open("scratch/verifier-w5alg1/out/kern_%s.txt" % fmt) as fh:
    for line in fh:
        tk = line.split()
        if len(tk) != 6 or tk[0] != "K":
            print("MALFORMED:", line[:80])
            continue
        _, f, inhx, mode, outhx, flhx = tk
        x = int(inhx, 16)
        mode = int(mode)
        got = (int(outhx, 16), int(flhx, 16))
        want = mydec.decide(f, x)[mode]
        c = cls_of(f, x)
        cls_tot[c] = cls_tot.get(c, 0) + 1
        total += 1
        if got != want:
            mism += 1
            cls_mis[c] = cls_mis.get(c, 0) + 1
            if shown < 15:
                shown += 1
                print("MISMATCH %s in=%x mode=%d got=%x/%02x want=%x/%02x"
                      % (f, x, mode, got[0], got[1], want[0], want[1]))
print("VOLUME %s vs own decider: total=%d mismatches=%d" % (fmt, total, mism))
print("by class totals:", sorted(cls_tot.items()))
print("by class mismatches:", sorted(cls_mis.items()))
print("ties seen: %d" % len(mydec.TIES_SEEN))
print("elapsed %.1fs" % (time.time() - t0))
