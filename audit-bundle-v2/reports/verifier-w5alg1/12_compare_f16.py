"""12_compare_f16.py - compare kernel sweep vs my decider, print counts."""
import importlib.util
import time

t0 = time.time()
_spec = importlib.util.spec_from_file_location(
    "mydec", "scratch/verifier-w5alg1/10_mydecider.py")
mydec = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mydec)

total = 0
mism = 0
ties = 0
ta_ne_te = 0
te_by_class = {}
shown = 0
with open("scratch/verifier-w5alg1/out/kern_f16.txt") as fh:
    for line in fh:
        tk = line.split()
        if len(tk) != 6 or tk[0] != "K":
            print("MALFORMED KERNEL LINE:", line[:80])
            continue
        _, fmt, inhx, mode, outhx, flhx = tk
        x = int(inhx, 16)
        mode = int(mode)
        got = (int(outhx, 16), int(flhx, 16))
        want = mydec.decide(fmt, x)[mode]
        total += 1
        if got != want:
            mism += 1
            if shown < 20:
                shown += 1
                print("MISMATCH f16 in=%04x mode=%d got=%04x/%02x want=%04x/%02x"
                      % (x, mode, got[0], got[1], want[0], want[1]))
print("F16-EXHAUSTIVE vs own decider: total=%d mismatches=%d" % (total, mism))
print("own-decider ties seen on f16 sweep: %d" % len(mydec.TIES_SEEN))
print("elapsed %.1fs" % (time.time() - t0))
