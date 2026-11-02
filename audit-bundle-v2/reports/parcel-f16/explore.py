import csv, collections, pathlib
wt = pathlib.Path("worktrees/w2-f16")
rows=[]
with open(wt/"docs/COVERAGE.tsv", newline="") as f:
    lines=[l for l in f if not l.startswith("#")]
rdr=csv.DictReader(lines, delimiter="\t")
print("fields", rdr.fieldnames)
for r in rdr:
    # wave column name?
    rows.append(r)
print("total", len(rows))
# print first row
print(rows[0])
# filter wave=2 msf16_
def w(r): return (r.get("wave") or r.get("Wave") or "").strip()
def n(r): return (r.get("name") or r.get("instantiation") or r.get("function") or "").strip()
# discover
for k in rows[0].keys(): print(repr(k), repr(rows[0][k]))
sel=[r for r in rows if w(r)=="2" and n(r).startswith("msf16_")]
print("sel", len(sel))
print(collections.Counter(r.get("authority","?") for r in sel))
print(collections.Counter(r.get("status","?") for r in sel))
for r in sel: print("\t".join(str(r[k]) for k in rdr.fieldnames))
