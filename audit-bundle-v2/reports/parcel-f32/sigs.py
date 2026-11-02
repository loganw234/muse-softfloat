import csv, re, pathlib
root=pathlib.Path("worktrees/w1-f32")
lines=[l for l in open(root/"docs/COVERAGE.tsv", encoding='utf-8').read().splitlines() if not l.startswith('#')]
rows=list(csv.DictReader(lines, delimiter='\t'))
mine=[r['name'] for r in rows if r['wave']=='1' and r['name'].startswith('msf32_')]
hdr=open(root/"include/muse_softfloat.h", encoding='utf-8').read()
# declarations end with ;
decls=re.findall(r'[^;\n]*\b(msf32_\w+)\s*\([^;]*\);', hdr, flags=re.S)
# simpler: split lines
out=[]
for name in mine:
    m=re.search(rf'^.*\b{re.escape(name)}\s*\(.*\);.*$', hdr, flags=re.M)
    out.append(m.group(0).strip() if m else f"MISSING {name}")
print("\n".join(out))
print("count", len(mine), "missing", sum(1 for o in out if o.startswith("MISSING")))
# also header prologue types flags rounding invalid rule
print("\n--- prologue up to first msf32 ---")
print(hdr[:hdr.find("msf32_round") if "msf32_round" in hdr else 6000])
