import pathlib, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
def totals(path):
    raw = pathlib.Path(path).read_bytes()
    t = raw.decode("utf-16", errors="replace") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", errors="replace")
    out=[]
    for m in re.finditer(r"total (\d+) passed (\d+) failed (\d+) malformed (\d+) skipped-planned (\d+)", t):
        out.append(tuple(int(x) for x in m.groups()))
    provs = re.findall(r"^prov (\S+) (\d+)", t, re.M)
    return out, provs

for name, path in [
    ("step2", "scratch/parcel-f64/regate-step2.outer.log"),
    ("step3", "scratch/parcel-f64/regate-step3.outer.log"),
    ("step45_final", "scratch/parcel-f64/regate-step45-final.outer.log"),
]:
    tot, prov = totals(path)
    s = [sum(x[i] for x in tot) for i in range(5)]
    print(name, "verify-runs:", len(tot), "sum total/passed/failed/malformed/skipped:", s)
    agg={}
    for k,v in prov: agg[k]=agg.get(k,0)+int(v)
    for k in sorted(agg): print("  prov", k, agg[k])

# berkeley regate arithmetic check
print("berkeley regate expected:", 8*46464 + 2000000 + 4*2000000 + 46464)
print("directed new total:", 3984+3264+1222+2302+285)
print("sweeps:", 210000+150000+120000)
wt=pathlib.Path("worktrees/w1-f64")
vecs=sorted((wt/"tests/vectors").glob("*f64*.vec"))
tot=0
for v in vecs:
    b=v.stat().st_size; tot+=b
    n=sum(1 for line in v.read_bytes().splitlines() if line and not line.startswith(b"#"))
    print(v.name, "cases", n, "bytes", b)
print("committed f64 vec bytes total", tot)
for f in ["src/msf64.c","tests/gen_vectors_f64.py"]:
    print(f, "lines", len((wt/f).read_text(encoding='utf-8').splitlines()))
