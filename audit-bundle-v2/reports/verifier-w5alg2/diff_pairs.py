#!/usr/bin/env python3
"""diff_pairs.py - differential drivers for verifier-w5alg2.

Subcommands (all counts printed):
  mydec-vs-mpfr : MY decider vs MPFR alg_decider on finite pairs
                  (kernel-independent validation of mydecide.py).
  kernel-floor  : kernel floor build vs MY decider (the real gate).
  kernel-jam    : kernel JAM build vs MY decider.
Writes pair files under out/ so kernel runs reuse identical inputs.
"""
import random
import subprocess
import sys

ROOT = "."
OUT = "scratch/verifier-w5alg2/out"
EXE_MPFR = OUT + "/alg_decider.exe"
EXE_FLOOR = OUT + "/harness_floor.exe"
EXE_JAM = OUT + "/harness_jam.exe"
MYDEC = "scratch/verifier-w5alg2/mydecide.py"
PY = None

import os
PY = os.environ.get("MSF_PYTHON", "python")

FMTS = {0: ("msf16_hypot", 16), 1: ("msf32_hypot", 32), 2: ("msf64_hypot", 64)}
OP_OF = {16: "msf16_hypot", 32: "msf32_hypot", 64: "msf64_hypot"}


def run(exe, args, stdin_text):
    p = subprocess.run([exe] + args, input=stdin_text, capture_output=True,
                       text=True)
    if p.returncode != 0:
        raise RuntimeError(f"{exe} {args} rc={p.returncode}: {p.stderr[-2000:]}")
    return p.stdout


def finite_pair(rng, w):
    emaxf = (1 << (w - 1 - (10 if w == 16 else 23 if w == 32 else 52))) - 1
    t = 10 if w == 16 else 23 if w == 32 else 52
    while True:
        a = rng.getrandbits(w)
        if ((a >> t) & emaxf) == emaxf:
            continue
        b = rng.getrandbits(w)
        if ((b >> t) & emaxf) == emaxf:
            continue
        return a, b


def check_equal(tag, pairs_by_fmt, lhs_lines, rhs_lines):
    n = mm = 0
    first = []
    for (fi, a, b), lline, rline in zip(
            [p for ps in pairs_by_fmt for p in ps], lhs_lines, rhs_lines):
        n += 5
        lt, rt = lline.split(), rline.split()
        for i in range(5):
            lb, lf = int(lt[2 * i], 16), int(lt[2 * i + 1], 16)
            rb, rf = int(rt[2 * i], 16), int(rt[2 * i + 1], 16)
            if lb != rb or lf != rf:
                mm += 1
                if len(first) < 5:
                    first.append((fi, a, b, i, lb, lf, rb, rf))
    print(f"{tag}: decisions={n} mismatches={mm} "
          f"{'PASS' if mm == 0 else 'FAIL'}")
    for fi, a, b, i, lb, lf, rb, rf in first:
        print(f"  fi={fi} a={a:x} b={b:x} rm={i} "
              f"lhs={lb:x}/{lf:02x} rhs={rb:x}/{rf:02x}")
    return mm


def sub_mydec_vs_mpfr():
    rng = random.Random(0x5eed16)
    allok = True
    for fi, (op, w) in FMTS.items():
        pairs = [finite_pair(rng, w) for _ in range(20000)]
        with open(f"{OUT}/s02_f{op[3:]}_pairs.txt", "w") as fh:
            for a, b in pairs:
                fh.write(f"{fi} {a:x} {b:x}\n")
        dec_in = "".join(f"{op} {a:x} {b:x}\n" for a, b in pairs)
        mpfr_out = run(EXE_MPFR, ["decide"], dec_in).splitlines()
        my_out = run(PY, [MYDEC, "decide"],
                     "".join(f"{fi} {a:x} {b:x}\n" for a, b in pairs)
                     ).splitlines()
        assert len(mpfr_out) == len(my_out) == len(pairs), \
            (len(mpfr_out), len(my_out), len(pairs))
        # mpfr lines: "op a b rb0 rf0 ..."; mydec lines: "rb0 rf0 ..."
        mpfr_norm = [" ".join(l.split()[3:]) for l in mpfr_out]
        mm = check_equal(f"mydec-vs-mpfr {op}",
                         [[(fi, a, b) for a, b in pairs]],
                         my_out, mpfr_norm)
        allok = allok and mm == 0
    print("OVERALL", "PASS" if allok else "FAIL")
    return 0 if allok else 1


def sub_kernel(which):
    exe = EXE_FLOOR if which == "kernel-floor" else EXE_JAM
    rng = random.Random(0x5eed16)
    allmm = 0
    for fi, (op, w) in FMTS.items():
        pairs = [finite_pair(rng, w) for _ in range(20000)]
        k_in = "".join(f"{fi} {a:x} {b:x}\n" for a, b in pairs)
        k_out = run(exe, ["hypot"], k_in).splitlines()
        my_out = run(PY, [MYDEC, "decide"], k_in).splitlines()
        mm = check_equal(f"{which} {op}",
                         [[(fi, a, b) for a, b in pairs]], k_out, my_out)
        allmm += mm
    print("OVERALL", "PASS" if allmm == 0 else "FAIL")
    return 0 if allmm == 0 else 1


if __name__ == "__main__":
    sub = sys.argv[1]
    if sub == "mydec-vs-mpfr":
        sys.exit(sub_mydec_vs_mpfr())
    if sub in ("kernel-floor", "kernel-jam"):
        sys.exit(sub_kernel(sub))
    raise SystemExit("unknown subcommand")
