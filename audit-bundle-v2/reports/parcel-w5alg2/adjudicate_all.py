"""Adjudicate ALL cr_hypot tp disagreements: emit decider input,
then (mode=check) compare MPFR decider tp vs exact-py tp vs cr."""
import pathlib
import sys

WS = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
S = WS / "scratch" / "parcel-w5alg2"
sys.path.insert(0, str(WS / "worktrees" / "w5-alg2" / "tests"))
import gen_vectors_alg as G  # noqa: E402

if sys.argv[1] == "gen":
    rows = []
    for ln in (S / "out" / "cm_hypot_out_U.txt").read_text().splitlines():
        t = ln.split()
        fmt, a, b, out = t[0], int(t[1], 16), int(t[2], 16), int(t[3], 16)
        exp = G.hypot_exact_decide(fmt, a, b)[G.RMS.index("tp")][0]
        if exp != out:
            rows.append((fmt, a, b, out, exp))
    with open(S / "out" / "adjudicate_all_in.txt", "w", newline="\n") as fh:
        for fmt, a, b, _, _ in rows:
            fh.write(f"msf{fmt[1:]}_hypot {a:x} {b:x}\n")
    with open(S / "out" / "adjudicate_all_expect.txt", "w", newline="\n") as fh:
        for fmt, a, b, cr, exp in rows:
            fh.write(f"{fmt} {a:x} {b:x} {cr:x} {exp:x}\n")
    print(f"disagreements: {len(rows)}")
else:
    exp_rows = []
    for ln in (S / "out" / "adjudicate_all_expect.txt").read_text().splitlines():
        t = ln.split()
        exp_rows.append((t[0], t[1], t[2], int(t[3], 16), int(t[4], 16)))
    dec = {}
    for ln in (S / "out" / "adjudicate_all_dec.txt").read_text().splitlines():
        t = ln.split()
        fmt = {"msf16_hypot": "f16", "msf32_hypot": "f32",
               "msf64_hypot": "f64"}[t[0]]
        dec[(fmt, t[1], t[2])] = int(t[7], 16)  # tp bits (3rd pair)
    mpfr_exact = cr_outlier = other = 0
    for fmt, a, b, cr, exp in exp_rows:
        m = dec[(fmt, a, b)]
        if m == exp:
            mpfr_exact += 1
            if m != cr:
                cr_outlier += 1
        else:
            other += 1
            print(f"MPFR!=exact {fmt} {a} {b} mpfr={m:x} exact={exp:x} cr={cr:x}")
    print(f"total={len(exp_rows)} mpfr==exact={mpfr_exact} "
          f"cr_outlier={cr_outlier} other={other}")
