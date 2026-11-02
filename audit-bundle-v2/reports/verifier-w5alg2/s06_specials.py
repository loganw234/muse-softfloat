#!/usr/bin/env python3
"""s06_specials.py - whole specials table, both operand orders.

Expectations are hard-coded from study Sec. 5.2 (evaluation order),
NOT from mydecide: sNaN first (first sNaN quieted + invalid), then
any inf -> +inf (incl. other operand qNaN, either order), then first
qNaN (exact bits, no flag), then both-zero -> +0. Kernel via harness.
Payloads and signs checked bit-exact; flags exact.
"""
import subprocess
import sys
import os

OUT = "scratch/verifier-w5alg2/out"
EXE = OUT + "/harness_floor.exe"
RMS = ("te", "tz", "tp", "tn", "ta")
INV = 0x01


def fmt_params(w):
    t = 10 if w == 16 else 23 if w == 32 else 52
    ew = w - 1 - t
    return dict(w=w, t=t, sign=1 << (w - 1),
                inf=((1 << ew) - 1) << t,
                qbit=1 << (t - 1),
                maxpay=(1 << t) - 1,
                mask=(1 << w) - 1)


CASES = []  # (fi, a, b, want_bits, want_flags, label)


def build():
    for fi, w in ((0, 16), (1, 32), (2, 64)):
        p = fmt_params(w)
        S, INF, QB = p["sign"], p["inf"], p["qbit"]
        MP = p["maxpay"]
        # sNaN samples (exp=all-ones, frac!=0, quiet=0), payloads+signs
        snans = [INF | 1, INF | (MP & ~QB), S | INF | 1, S | INF | (MP & ~QB)]
        # qNaN samples (exp=all-ones, quiet=1), payloads+signs
        qnans = [INF | QB, INF | QB | 1, INF | MP, S | INF | QB,
                 S | INF | QB | 5]
        fins = [0x3c00 & p["mask"] if w == 16 else
                (0x3f800000 if w == 32 else 0x3ff0000000000000),
                0x0001, p["mask"] >> 1 & MP]  # 1.0, min subnormal, max subnormal frac
        # 1) sNaN first, both orders, against every class
        others = snans + qnans + [INF, INF | S, 0, S,
                                  fins[0], fins[0] | S]
        for s_ in snans:
            for o in others:
                for a, b in ((s_, o), (o, s_)):
                    # first-sNaN rule resolved in main()
                    CASES.append((fi, a & p["mask"], b & p["mask"], None, INV,
                                  "snan-first"))
        # 2) inf over qNaN/finite/zero/inf, both orders (no sNaN here)
        for o in qnans + [INF, INF | S, 0, S, fins[0], fins[0] | S]:
            for a, b in ((INF, o), (o, INF), (INF | S, o), (o, INF | S)):
                CASES.append((fi, a & p["mask"], b & p["mask"], INF, 0,
                              "inf-over"))
        # 3) qNaN matrix, both orders, payloads exact
        for q in qnans:
            for o in qnans + [0, S, fins[0], fins[1]]:
                for a, b in ((q, o), (o, q)):
                    # first-qNaN rule resolved in main()
                    CASES.append((fi, a & p["mask"], b & p["mask"], None, 0,
                                  "qnan-matrix"))
        # 4) signed zeros -> +0 all four combos
        for a, b in ((0, 0), (0, S), (S, 0), (S, S)):
            CASES.append((fi, a, b, 0, 0, "zero-pair"))


def is_nan_cls(w, x):
    """(is_nan, is_signaling) for a same-format encoding."""
    p = fmt_params(w)
    ew = w - 1 - p["t"]
    if ((x >> p["t"]) & ((1 << ew) - 1)) != ((1 << ew) - 1):
        return False, False
    if (x & p["maxpay"]) == 0:
        return False, False
    return True, (x & p["qbit"]) == 0


def is_qnan(w, x):
    nan, sig = is_nan_cls(w, x)
    return nan and not sig


def main():
    build()
    # resolve NaN-matrix expectations: first sNaN / first qNaN wins
    resolved = []
    for fi, a, b, want, fl, label in CASES:
        w = 16 if fi == 0 else 32 if fi == 1 else 64
        p = fmt_params(w)
        if label == "snan-first":
            na_sa, sig_a = is_nan_cls(w, a)
            na_sb, sig_b = is_nan_cls(w, b)
            first = a if (na_sa and sig_a) else b
            assert (na_sa and sig_a) or (na_sb and sig_b)
            want = (first | p["qbit"]) & p["mask"]
        if label == "qnan-matrix":
            qa, qb = is_qnan(w, a), is_qnan(w, b)
            want = (a if qa else b) & ((1 << w) - 1)
            assert qa or qb
        resolved.append((fi, a, b, want, fl, label))
    blob = "".join(f"{fi} {a:x} {b:x}\n" for fi, a, b, _, _, _ in resolved)
    kh = subprocess.run([EXE, "hypot"], input=blob, capture_output=True,
                        text=True)
    if kh.returncode != 0:
        raise RuntimeError(kh.stderr[-2000:])
    kl = kh.stdout.splitlines()
    assert len(kl) == len(resolved)
    total = mm = 0
    by_label = {}
    first = []
    for (fi, a, b, want, fl, label), line in zip(resolved, kl):
        kt = line.split()
        for i in range(5):
            lb, lf = int(kt[2 * i], 16), int(kt[2 * i + 1], 16)
            total += 1
            ok = (lb == want and lf == fl)
            by_label.setdefault(label, [0, 0])
            by_label[label][0] += 1
            if not ok:
                mm += 1
                by_label[label][1] += 1
                if len(first) < 12:
                    first.append((fi, a, b, i, lb, lf, want, fl, label))
    print(f"SPECIALS: cases={len(resolved)} decisions={total} "
          f"mismatches={mm} {'PASS' if mm == 0 else 'FAIL'}")
    for label, (n, m) in by_label.items():
        print(f"  {label}: decisions={n} mismatches={m}")
    for fi, a, b, i, lb, lf, want, fl, label in first:
        print(f"  [{label}] fi={fi} a={a:x} b={b:x} rm={RMS[i]} "
              f"kernel={lb:x}/{lf:02x} want={want:x}/{fl:02x}")
    return 0 if mm == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
