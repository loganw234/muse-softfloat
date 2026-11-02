import pathlib, re, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
logs=sorted(pathlib.Path("worktrees/w1-f64/build/w1/logs").glob("*.verify.log"))
pat=re.compile(r"^FAIL .* got ([0-9a-f]+)/([0-9a-f]+) want ([0-9a-f]+)/([0-9a-f]+)")
for p in logs:
    lines=p.read_text(errors="ignore").splitlines()
    fails=[l for l in lines if l.startswith("FAIL")]
    if not fails: continue
    kinds=collections.Counter()
    for l in fails:
        m=pat.match(l)
        if not m: kinds["unparsed"]+=1; continue
        got,gf,want,wf=m.groups()
        if got!=want and gf!=wf: k="bits+flags"
        elif got!=want: k="bits-only"
        elif gf!=wf: k=f"flags-only {gf}->{wf}"
        else: k="same?"
        kinds[k]+=1
    print(p.name, len(fails), dict(kinds))
    for l in fails[:2]: print("   ",l[:220])
