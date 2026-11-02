"""cr_hypot execution corroboration driver.

gen: extract unique finite hypot pairs from the committed
alg-*.vec sections + seeded finite pairs, write cases file.
check: compare harness outputs (4 fenv modes) against the
generator's exact decider, bits only.
"""
import pathlib
import random
import sys

WS = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
S = WS / "scratch" / "parcel-w5alg2"
sys.path.insert(0, str(WS / "worktrees" / "w5-alg2" / "tests"))
import gen_vectors_alg as G  # noqa: E402

FMTS = ("f16", "f32", "f64")


def finite_pairs():
    pairs = {f: set() for f in FMTS}
    for fmt in FMTS:
        path = WS / "worktrees/w5-alg2/tests/vectors" / f"alg-{fmt}.vec"
        for ln in path.read_text().splitlines():
            t = ln.split()
            if len(t) == 8 and "_hypot" in t[0] and t[1] == "te":
                a, b = int(t[2], 16), int(t[3], 16)
                if G.cls_of(fmt, a) == "finite" and G.cls_of(fmt, b) == "finite":
                    pairs[fmt].add((a, b))
        rng = random.Random(20261031 + int(fmt[1:]))
        q = G.params(fmt)
        while len(pairs[fmt]) < 4000:
            a = rng.getrandbits(q["bits"])
            b = rng.getrandbits(q["bits"])
            if G.cls_of(fmt, a) == "finite" and G.cls_of(fmt, b) == "finite":
                pairs[fmt].add((a, b))
    return pairs


def gen():
    pairs = finite_pairs()
    with open(S / "out" / "cm_hypot_cases.txt", "w", newline="\n") as fh:
        for fmt in FMTS:
            for a, b in sorted(pairs[fmt]):
                fh.write(f"{fmt} {a:x} {b:x}\n")
    print({f: len(pairs[f]) for f in FMTS})


def check():
    mode_of = {"N": "te", "Z": "tz", "U": "tp", "D": "tn"}
    total = bad = 0
    for mletter, rm in mode_of.items():
        path = S / "out" / f"cm_hypot_out_{mletter}.txt"
        for ln in path.read_text().splitlines():
            t = ln.split()
            fmt, a, b, out = t[0], int(t[1], 16), int(t[2], 16), int(t[3], 16)
            exp = G.hypot_exact_decide(fmt, a, b)[G.RMS.index(rm)][0]
            total += 1
            if exp != out:
                bad += 1
                if bad <= 10:
                    print(f"DISAGREE {fmt} {rm} a={a:x} b={b:x} "
                          f"cr={out:x} exact={exp:x}")
    print(f"CM-HYPOT checked={total} disagreements={bad} "
          f"{'PASS' if bad == 0 else 'FAIL'}")
    return 1 if bad else 0


if __name__ == "__main__":
    if sys.argv[1] == "gen":
        gen()
    else:
        sys.exit(check())
