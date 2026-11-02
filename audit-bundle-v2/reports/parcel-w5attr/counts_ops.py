#!/usr/bin/env python3
"""Per-op-family ta census over committed vectors: ta lines and
ta-vs-te tie witnesses grouped by operation family (op name with
format suffixes stripped to the family stem)."""
import pathlib
import re
import sys
from collections import Counter

RMS = ("te", "tz", "tp", "tn", "ta", "-")

# family stem: strip msfNN_ prefix and trailing _fNN format parts
def fam(op):
    op = re.sub(r"^msf(16|32|64)_", "", op)
    op = re.sub(r"(_f(16|32|64))+$", "", op)
    return op


def main():
    root = pathlib.Path(sys.argv[1])
    ta_c = Counter()
    wit_c = Counter()
    ops_ta = Counter()
    outcome = {}
    for path in sorted(root.glob("*.vec")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#"):
                continue
            tok = line.split()
            if len(tok) < 3 or tok[1] not in RMS or "->" not in tok:
                continue
            i = tok.index("->")
            key = (tok[0], tuple(tok[2:i]))
            outcome[(key, tok[1])] = tuple(tok[i + 1:-1])
            if tok[1] == "ta":
                ta_c[fam(tok[0])] += 1
                ops_ta[tok[0]] += 1
    for (key, rm), out in outcome.items():
        if rm == "ta" and (key, "te") in outcome and outcome[(key, "te")] != out:
            wit_c[fam(key[0])] += 1
    print("%-28s %8s %8s" % ("family", "ta", "wit"))
    for f in sorted(ta_c):
        print("%-28s %8d %8d" % (f, ta_c[f], wit_c[f]))
    print("distinct ops with ta lines:", len(ops_ta))
    print("ops with ta but zero witnesses (sample):")
    zw = [o for o in sorted(ops_ta)]
    # per-op witnesses
    opwit = Counter()
    for (key, rm), out in outcome.items():
        if rm == "ta" and (key, "te") in outcome and outcome[(key, "te")] != out:
            opwit[key[0]] += 1
    zeros = [o for o in zw if opwit[o] == 0]
    print(" ", len(zeros), "ops:", ", ".join(zeros[:60]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
