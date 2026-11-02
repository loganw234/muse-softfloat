import pathlib, re, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
root=pathlib.Path("worktrees/w1-f64")
logs=sorted((root/"build/w1/logs").glob("*.verify.log"))
tot=re.compile(r"^total (\d+) passed (\d+) failed (\d+) malformed (\d+) skipped-planned (\d+)")
rows=[]
for p in logs:
    txt=p.read_text(errors="ignore").splitlines()
    m=None; verdict=""
    for l in txt:
        mm=tot.match(l)
        if mm: m=[int(x) for x in mm.groups()]
        if l.startswith("VERDICT"): verdict=l
    if m:
        rows.append((p.name,)+tuple(m)+(verdict,))
for r in rows:
    print("\t".join(str(x) for x in r))
print("FILES", len(rows))
print("SUM total/passed/failed/skipped",
      sum(r[1] for r in rows), sum(r[2] for r in rows),
      sum(r[3] for r in rows), sum(r[5] for r in rows))
