import os, sys
ROOT = sys.argv[1]
vdir = os.path.join(ROOT, "tests", "vectors")
total = data = comments = blank = 0
for f in sorted(os.listdir(vdir)):
    if not f.endswith(".vec"):
        continue
    for ln in open(os.path.join(vdir, f), encoding="utf-8", errors="replace"):
        total += 1
        s = ln.strip()
        if not s:
            blank += 1
        elif s.startswith("#"):
            comments += 1
        else:
            data += 1
print(f"vectors total={total} data={data} comments={comments} blank={blank}")
cat = [ln for ln in open(os.path.join(ROOT, "tests", "interval_catalogue.tsv"), encoding="utf-8")]
datarows = [ln for ln in cat if ln.strip() and not ln.startswith("#")]
print(f"catalogue lines={len(cat)} noncomment={len(datarows)} header={datarows[0].strip()[:100]!r} rows_excl_header={len(datarows)-1}")
# how site/build_data.py counts vectors
src = open(os.path.join(ROOT, "site", "build_data.py"), encoding="utf-8").read()
import re
for i, ln in enumerate(src.splitlines(), 1):
    if "count" in ln.lower() or ".vec" in ln:
        print(f"build_data.py:{i}: {ln.strip()}")
# run.sh inventory vector counting refs
rs = open(os.path.join(ROOT, "tools", "run.sh"), encoding="utf-8").read()
for i, ln in enumerate(rs.splitlines(), 1):
    if re.search(r"411213|1117504|5505024|vectors.*count|wc -l", ln):
        print(f"run.sh:{i}: {ln.strip()}")
