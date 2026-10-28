#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""compare_ias15.py - step-by-step IAS15FH1 hash comparison.

Usage: compare_ias15.py <expected-file> <candidate-file>

Both files hold IAS15FH1 rows, one per step:
  <step> <H_state> <H_full> <t bits> <dt bits> <dt_last_done bits>
Comment lines (starting with #) are ignored for the row
comparison, except that the candidate must carry an "# END" line
reporting nonfinite_hashed_fields=0 - a NaN or infinity reaching
hashed state can never pass silently, whatever the rows say.

Prints steps_compared/matched/first_divergence and a final
"COMPARE PASS" or "COMPARE FAIL".  Exit 0 iff every expected row
is present and identical in the candidate (and vice versa) and
the non-finite count is zero.  This is also the comparator the
demo's board stage hands to board/ias15_run.sh as IAS15_COMPARE.
"""
import re
import sys

END_NONFINITE = re.compile(r"nonfinite_hashed_fields=(\d+)")


def load(path):
    rows = {}
    end_nonfinite = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                m = END_NONFINITE.search(line)
                if m:
                    end_nonfinite = int(m.group(1))
                continue
            fields = line.split()
            rows[int(fields[0])] = tuple(fields[1:])
    return rows, end_nonfinite


def main(argv):
    if len(argv) != 3:
        print("usage: compare_ias15.py <expected> <candidate>")
        return 2
    expected, _ = load(argv[1])
    candidate, cand_nonfinite = load(argv[2])
    keys = sorted(set(expected) | set(candidate))
    matched = 0
    first_divergence = None
    for k in keys:
        if k not in expected or k not in candidate:
            print("MISSING step %d (expected=%s candidate=%s)"
                  % (k, k in expected, k in candidate))
            first_divergence = k
            break
        if expected[k] != candidate[k]:
            print("DIVERGE step %d" % k)
            print("  expected :", expected[k])
            print("  candidate:", candidate[k])
            first_divergence = k
            break
        matched += 1
    print("steps_compared=%d matched=%d first_divergence=%s"
          % (len(keys), matched, first_divergence))
    ok = first_divergence is None and matched == len(keys) and keys
    if cand_nonfinite is None:
        print("candidate has no '# END nonfinite_hashed_fields=' line")
        ok = False
    elif cand_nonfinite != 0:
        print("candidate nonfinite_hashed_fields=%d (must be 0)"
              % cand_nonfinite)
        ok = False
    print("COMPARE %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
