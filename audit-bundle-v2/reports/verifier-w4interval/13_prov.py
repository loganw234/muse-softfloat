#!/usr/bin/env python3
# 13_prov.py - every catalogue row carries provenance; ids 1..710, 710 rows.
T = "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-interval/tests/interval_catalogue.tsv"
ids, badprov, kinds = [], 0, {}
n = 0
with open(T) as fh:
    for ln in fh:
        if ln.startswith("#") or not ln.strip():
            continue
        n += 1
        p = ln.rstrip("\n").split("\t")
        ids.append(int(p[0]))
        kinds[p[2]] = kinds.get(p[2], 0) + 1
        if len(p) != 19 or not p[3].strip():
            badprov += 1
            print("BAD ROW:", p[0])
print("data rows:", n, "ids 1..710 contiguous:", ids == list(range(1, 711)))
print("kinds:", kinds, "rows missing provenance:", badprov)
