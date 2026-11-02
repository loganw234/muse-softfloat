#!/usr/bin/env python3
"""Per-file rm census + ta-vs-te tie witnesses for committed vectors.

A tie witness: a ta line and a te line with the same op and same
operand tokens (everything between rm and '->') whose outcome
tokens after '->' (excluding provenance, the last token) differ.
For string vectors the operand tokens include IN=/A=/SPEC= and the
outcome includes OUT=/bits/flags/C=, so the same rule applies.
Usage: counts.py VECDIR
"""
import pathlib
import sys
from collections import Counter, defaultdict

RMS = ("te", "tz", "tp", "tn", "ta", "-")


def main():
    root = pathlib.Path(sys.argv[1])
    tot_rm = Counter()
    tot_ta = tot_wit = 0
    print("%-24s %7s %7s %7s %7s %7s %7s %8s" %
          ("file", "lines", "te", "tz/tp/tn", "ta", "ta-wit", "-", ""))
    for path in sorted(root.glob("*.vec")):
        rm_c = Counter()
        outcome = {}  # (op, operands, rm) -> outcome string
        n = 0
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#"):
                continue
            tok = line.split()
            if len(tok) < 3 or tok[1] not in RMS:
                continue
            n += 1
            rm_c[tok[1]] += 1
            if "->" in tok:
                i = tok.index("->")
                key = (tok[0], tuple(tok[2:i]))
                outcome[(key, tok[1])] = tuple(tok[i + 1:-1])
        wit = 0
        for (key, rm), out in outcome.items():
            if rm == "ta" and (key, "te") in outcome and outcome[(key, "te")] != out:
                wit += 1
        tot_rm.update(rm_c)
        tot_ta += rm_c["ta"]
        tot_wit += wit
        if rm_c["ta"] or rm_c["te"]:
            print("%-24s %7d %7d %7d %7d %7d %7d" %
                  (path.name, n, rm_c["te"],
                   rm_c["tz"] + rm_c["tp"] + rm_c["tn"],
                   rm_c["ta"], wit, rm_c["-"]))
    print("TOTAL rm:", dict(tot_rm))
    print("TOTAL ta lines:", tot_ta, " ta-vs-te tie witnesses:", tot_wit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
