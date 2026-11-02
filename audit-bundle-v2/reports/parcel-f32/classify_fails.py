import pathlib, re, collections
for p in sorted(pathlib.Path("scratch/parcel-f32/berkeley-logs").glob("*.log")):
    ls=[l for l in p.read_text(errors='replace').splitlines() if l.startswith("FAIL")]
    kinds=collections.Counter()
    resdiff=0
    for l in ls:
        m=re.search(r"got ([0-9a-f]+)/([0-9a-f]+) want ([0-9a-f]+)/([0-9a-f]+)",l)
        if m:
            kinds[(m.group(2),m.group(4))]+=1
            if m.group(1)!=m.group(3): resdiff+=1
    print(p.name, len(ls), dict(kinds), "result-differs:", resdiff)
    for l in ls[:3]:
        print("   ", l[l.find("|")+2:][:150])
log=pathlib.Path("scratch/parcel-f32/berkeley-results.log").read_text()
for l in log.splitlines():
    if "sqrt" in l and "l1 " in l or "roundToInt-te" in l or "f64_to_f32-te" in l or "to_i32-te" in l or "i32_to_f32-te" in l:
        print(l[:160])
