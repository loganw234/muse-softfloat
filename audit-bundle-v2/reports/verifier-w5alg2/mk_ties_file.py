#!/usr/bin/env python3
"""mk_ties_file.py - extract tie pairs from s07 log into a harness file."""
import re

fi_of = {16: 0, 32: 1, 64: 2}
out = ["0 62c 67b", "0 67b 62c"]
seen = set(out)
for line in open("scratch/verifier-w5alg2/out/s07_ties.log"):
    m = re.search(r"\[euclid-f(\d+)\] fi=(\d+) a=([0-9a-f]+) b=([0-9a-f]+)", line)
    if m:
        key = f"{m.group(2)} {m.group(3)} {m.group(4)}"
        if key not in seen:
            seen.add(key)
            out.append(key)
with open("scratch/verifier-w5alg2/t_ties.txt", "w") as fh:
    fh.write("\n".join(out) + "\n")
print(f"wrote {len(out)} tie pairs")
