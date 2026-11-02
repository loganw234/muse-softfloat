import sys
from pathlib import Path
from collections import Counter
V = Path(sys.argv[1])
rows = []
for line in (V/"docs"/"COVERAGE.tsv").read_text().splitlines():
    if not line or line.startswith("#") or line.startswith("name\t"):
        continue
    rows.append(line.split("\t"))
print("rounding:", dict(Counter(f[5] for f in rows)))
print("flags:", dict(Counter(f[6] for f in rows)))
print("tier2 rounding:", dict(Counter(f[5] for f in rows if f[12]=="2")))
print("tier2 claim:", dict(Counter(f[13] for f in rows if f[12]=="2")))
print("wave:", dict(Counter(f[7] for f in rows)))
# fifth attribute = rows carrying caller rounding (not clause-fixed)?
fixed = [f for f in rows if f[5]=="fixed"]
print("rounding==fixed:", len(fixed), sorted(set(f[1] for f in fixed))[:20])
