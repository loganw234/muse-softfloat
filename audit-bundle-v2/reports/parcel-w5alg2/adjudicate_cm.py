"""Breakdown + adjudication sample for cm_hypot disagreements."""
import collections
import pathlib
import sys

WS = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
S = WS / "scratch" / "parcel-w5alg2"
sys.path.insert(0, str(WS / "worktrees" / "w5-alg2" / "tests"))
import gen_vectors_alg as G  # noqa: E402

mode_of = {"N": "te", "Z": "tz", "U": "tp", "D": "tn"}
brk = collections.Counter()
samples = []
for mletter, rm in mode_of.items():
    for ln in (S / "out" / f"cm_hypot_out_{mletter}.txt").read_text().splitlines():
        t = ln.split()
        fmt, a, b, out = t[0], int(t[1], 16), int(t[2], 16), int(t[3], 16)
        exp = G.hypot_exact_decide(fmt, a, b)[G.RMS.index(rm)][0]
        if exp != out:
            brk[(fmt, rm)] += 1
            if len(samples) < 12 and (fmt, rm) == ("f32", "tp"):
                samples.append((a, b, out, exp))
print("breakdown:", dict(brk))
with open(S / "out" / "adjudicate_in.txt", "w", newline="\n") as fh:
    for a, b, cr, exp in samples:
        fh.write(f"msf32_hypot {a:x} {b:x}\n")
        print(f"sample a={a:x} b={b:x} cr_tp={cr:x} exact_tp={exp:x}")
