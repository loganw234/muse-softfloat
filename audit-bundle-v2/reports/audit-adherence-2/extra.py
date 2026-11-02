#!/usr/bin/env python3
"""Extra probes: tracked tree, coverage status, key set, record numstat, copy shape. Read-only."""
import os, re, sys, json, hashlib, subprocess, csv
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO="muse-softfloat"; SAFE="C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat"
def git(*a, repo=REPO, safe=SAFE):
    r=subprocess.run(["git","-C",repo,"-c",f"safe.directory={safe}",*a],capture_output=True,text=True,encoding="utf-8",errors="replace")
    return (r.stdout+r.stderr).strip()
files=git("ls-files").splitlines()
print(f"tracked files: {len(files)}")
print("tracked by top:", dict(Counter(f.split('/')[0] if '/' in f else '(root)' for f in files)))
print("src/include tracked:", [f for f in files if f.startswith(("src/","include/"))])
markers=("Berkeley","SoftFloat","TestFloat","CORE-MATH","core-math","kiss_fft","KissFFT","REBOUND","Copyright")
for f in files:
    if f.startswith(("src/","include/","compat/")):
        t=open(os.path.join(REPO,f),encoding="utf-8",errors="replace").read()
        hits={m:t.count(m) for m in markers if t.count(m)}
        if hits: print(f"  TRACKED-SRC-MARKER {f}: {hits}")
print("any tracked path with 'key' or 'scratch':", [f for f in files if "key" in f.lower() or "scratch" in f.lower()][:10])
# coverage proper parse
rows=[l.rstrip("\n").split("\t") for l in open("muse-softfloat/docs/COVERAGE.tsv",encoding="utf-8",errors="replace") if not l.startswith("#")]
hdr=rows[0]; print("\nCOVERAGE header:", hdr)
for ci,h in enumerate(hdr):
    vals=Counter(r[ci] for r in rows[1:] if len(r)>ci)
    if len(vals)<=20: print(f" col {h}: {dict(vals)}")
# plants key set vs key files (hash only)
pj=[json.loads(l) for l in open("muse-softfloat/docs/metrics/plants.jsonl",encoding="utf-8") if l.strip()]
pset=set(r["key_sha256"] for r in pj)
kset={}
for fn in sorted(os.listdir("scratch/lead/keys")):
    if fn.startswith("key-"):
        kset[hashlib.sha256(open(os.path.join("scratch/lead/keys",fn),'rb').read()).hexdigest()]=fn
print(f"\nplants distinct keys={len(pset)} key files={len(kset)} plants-keys-not-on-disk={pset-set(kset)} disk-not-in-plants={set(kset)-pset}")
# record/metrics numstat deletions
for path in ("docs/RECORD.md","docs/metrics/passes.jsonl","docs/metrics/plants.jsonl","docs/metrics/briefs.jsonl","docs/metrics/usage.jsonl","docs/BOARD.md","README.md"):
    out=git("log","--numstat","--format=%h","main","--",path)
    print(f"\nnumstat {path}:")
    cur="?"
    for line in out.splitlines():
        if re.fullmatch(r"[0-9a-f]{7,40}",line.strip()): cur=line.strip()[:7]
        elif "\t" in line: print(f"  {cur} {line}")
# copy shape sample: 4 copies across waves
for name in ("verify-f32","verify2-f16","verify4-trig","verify5-attr"):
    p=f"worktrees/{name}"; safe=f"C:/Users/logan/source/repos/Muse-Softfloat/{p}"
    print(f"\nCOPY {p}: HEAD={git('log','-1','--format=%h %P %s',repo=p,safe=safe)[:120]}")
    print(f"  refs=[{git('for-each-ref',repo=p,safe=safe)}] remotes=[{git('remote',repo=p,safe=safe)}] branch=[{git('branch',repo=p,safe=safe)}]")
    print(f"  status-lines={len(git('status','--porcelain',repo=p,safe=safe).splitlines()) if git('status','--porcelain',repo=p,safe=safe) else 0}")
# run.sh controls
t=open("muse-softfloat/tools/run.sh",encoding="utf-8",errors="replace").read()
print("\nrun.sh lines:", t.count("\n"), " 'control' mentions:", len(re.findall(r"control",t,re.I)))
for i,l in enumerate(t.splitlines(),1):
    if re.search(r"control\s*\d|CONTROL|neg.*control",l,re.I): print(f"  run.sh:{i}: {l.strip()[:170]}")
