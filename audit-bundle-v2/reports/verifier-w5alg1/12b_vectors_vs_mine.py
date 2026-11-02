"""12b_vectors_vs_mine.py - my decider vs committed alg vectors (triangulation)."""
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "mydec", "scratch/verifier-w5alg1/10_mydecider.py")
mydec = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mydec)

MODES = ("te", "tz", "tp", "tn", "ta")
for fmt, path in (("f16", "worktrees/verify5-alg1/tests/vectors/alg-f16.vec"),
                  ("f32", "worktrees/verify5-alg1/tests/vectors/alg-f32.vec"),
                  ("f64", "worktrees/verify5-alg1/tests/vectors/alg-f64.vec")):
    total = mism = 0
    first = []
    with open(path) as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            tk = line.split()
            # op mode inhex -> outhex flags tag
            op, mode, inhx = tk[0], tk[1], tk[2]
            want = (int(tk[4], 16), int(tk[5], 16))
            got = mydec.decide(fmt, int(inhx, 16))[MODES.index(mode)]
            total += 1
            if got != want:
                mism += 1
                if len(first) < 5:
                    first.append((inhx, mode, got, want))
    print("mine-vs-committed %s: total=%d mismatches=%d" % (fmt, total, mism))
    for f in first:
        print("   ", f)
print("ties seen overall:", len(mydec.TIES_SEEN))
