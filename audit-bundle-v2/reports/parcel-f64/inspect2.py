import csv, pathlib
root=pathlib.Path("worktrees/w1-f64")
lines=[l for l in open(root/"docs/COVERAGE.tsv") if not l.startswith("#")]
rows=list(csv.DictReader(lines, delimiter="\t"))
print(rows[0].keys())
print(rows[0])
w1=[r for r in rows if r.get("wave")=="1" and r.get("name","").startswith("msf64_")]
print("COUNT", len(w1))
for r in w1:
    print("\t".join(r.values()))
# also msf32/msf16 logb? names start msf64 only per brief; but logB dest is msf64 returned by msf32_log_b etc - check if those counted elsewhere
print("--- all wave1 not msf64/msf32 sample")
others=[r for r in rows if r.get("wave")=="1" and not r.get("name","").startswith("msf64_") and not r.get("name","").startswith("msf32_")]
print(len(others), others[:20])
print("wave1 total", len([r for r in rows if r.get("wave")=="1"]))
