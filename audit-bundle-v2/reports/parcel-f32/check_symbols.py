import csv, pathlib, re, subprocess, sys
root=pathlib.Path("worktrees/w1-f32")
lines=[l for l in open(root/"docs/COVERAGE.tsv", encoding='utf-8').read().splitlines() if not l.startswith('#')]
rows=list(csv.DictReader(lines, delimiter='\t'))
mine=[r['name'] for r in rows if r['wave']=='1' and r['name'].startswith('msf32_')]
nm = sys.argv[1]
out = subprocess.run([nm, sys.argv[2]], capture_output=True, text=True).stdout
syms=set(re.findall(r'\b[0-9a-fA-F]*\s+[Tt]\s+_?(\w+)', out))
missing=[n for n in mine if n not in syms]
print("defined matching:", len(mine)-len(missing), "missing:", missing)
extra=[s for s in sorted(syms) if s.startswith('msf32_') and s not in mine]
print("extra msf32 symbols (wave0 performat expected):", extra)
print("total mine", len(mine))
