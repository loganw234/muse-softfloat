# Union-resolve tables/implemented.tsv: keep every non-conflict line,
# then both sides' conflict blocks (rows are append-only and disjoint
# by instantiation name; assert no duplicate names survive).
import pathlib
import sys

P = pathlib.Path("muse-softfloat/tables/implemented.tsv")
out, seen = [], set()
dupes = []
for line in P.read_text().splitlines():
    if line.startswith(("<<<<<<<", "=======", ">>>>>>>")):
        continue
    key = line.split("\t")[0] if line.strip() else ""
    if key and key in seen:
        dupes.append(key)
        continue
    if key:
        seen.add(key)
    out.append(line)
if dupes:
    print("DUPLICATES DROPPED:", dupes)
    sys.exit(1)
P.write_text("\n".join(out) + "\n")
print("rows:", len([l for l in out if l.strip()]))
