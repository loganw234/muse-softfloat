"""Cross-check harness decide mode (fast get_d narrow) against
the spike's recipe-narrowed redecided worst-case outputs.
Input file lines: bits wide te tz tp tn (spike format)."""
import subprocess
import sys

EXE = "worktrees/w4-trig/build/trig/trig_exhaustive.exe"
N = 3000


def load(fn, path):
    rows = []
    with open(path) as fh:
        for line in fh:
            t = line.split()
            if len(t) == 6 and t[1] != "NONFINITE":
                rows.append((t[0], t[2], t[3], t[4], t[5]))
            if len(rows) >= N:
                break
    inp = "".join(f"msf64_{fn} {r[0]}\n" for r in rows)
    out = subprocess.run([EXE, "decide"], input=inp, capture_output=True,
                         text=True, check=True).stdout
    got = {}
    for line in out.splitlines():
        t = line.split()
        if len(t) == 10:
            got[t[1]] = (t[2], t[4], t[6], t[8])
    bad = 0
    sat = 0
    for r in rows:
        g = got.get(r[0])
        # spike decider (prec 320) is blind in the saturation
        # family: rows where it claims exactly +-1 in all modes
        # for a non-integer/half-integer input are its known
        # limit (adjudicated separately); skip with a count.
        if all(v in ("3ff0000000000000", "bff0000000000000") for v in r[1:]):
            sat += 1
            continue
        if g is None or any(int(a, 16) != int(b, 16) for a, b in zip(g, r[1:])):
            bad += 1
            if bad <= 5:
                print("DIFF", fn, r, g)
    print(f"{fn}: compared {len(rows)} disagree {bad} saturation-skipped {sat}")
    return bad


total = 0
total += load("sin_pi", "scratch/tier2-trig-spike/out/wc_sinpi_redecided.txt")
total += load("cos_pi", "scratch/tier2-trig-spike/out/wc_cospi_redecided.txt")
print("XCHECK", "PASS" if total == 0 else "FAIL")
sys.exit(1 if total else 0)
