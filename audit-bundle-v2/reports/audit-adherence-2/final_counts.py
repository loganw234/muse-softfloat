#!/usr/bin/env python3
"""Final counts: ledger refs in FP bodies, checked_by values, RECORD tables, reveal search. Read-only."""
import subprocess, json, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO="muse-softfloat"; SAFE="C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat"
def git(*a):
    return subprocess.run(["git","-C",REPO,"-c",f"safe.directory={SAFE}",*a],capture_output=True,text=True,encoding="utf-8",errors="replace").stdout
fmt="%h%x1f%s%x1f%b%x1e"
recs=[r for r in git("log","--first-parent","main",f"--format={fmt}").split("\x1e") if r.strip()]
nol=[]; thin=[]
for r in recs:
    p=r.strip("\n").split("\x1f")
    if len(p)<3: continue
    h,s,b=p[0],p[1],p[2]
    if "ledger" not in b.lower(): nol.append(h)
    body_nc="\n".join(l for l in b.splitlines() if not l.startswith("Co-Authored-By")).strip()
    if len(body_nc)<200: thin.append((h,len(body_nc),s[:60]))
print(f"FP commits={len(recs)} without 'ledger' in body={len(nol)}: {nol}")
print(f"FP body (ex-trailer) <200 chars={len(thin)}")
for t in thin: print("  THIN",t)
pj=[json.loads(l) for l in open("muse-softfloat/docs/metrics/plants.jsonl",encoding="utf-8") if l.strip()]
from collections import Counter
print("plants checked_by:",Counter(r.get("checked_by") for r in pj),"graded_by:",Counter(r.get("graded_by") for r in pj))
rec=open("muse-softfloat/docs/RECORD.md",encoding="utf-8",errors="replace").read()
print("\nRECORD: kit-version/table markers:", {w:rec.lower().count(w) for w in ("round_metrics","kit softfloat-bootstrap-kit","sha256","chain","time box","sent back")})
for i,l in enumerate(rec.splitlines(),1):
    if re.search(r"fingerprint|waiv",l,re.I): print(f"  RECORD:{i}: {l.strip()[:180]}")
lead=open("ledger/lead.md",encoding="utf-8",errors="replace").read()
for i,l in enumerate(lead.splitlines(),1):
    if re.search(r"fingerprint|waiv|zip|reveal",l,re.I): print(f"  lead:{i}: {l.strip()[:180]}")
print("\nRECORD last 30 lines:")
print("\n".join(rec.splitlines()[-30:]))
print("\nRECORD rate context 555-575:")
print("\n".join(f"{i}: {l}" for i,l in enumerate(rec.splitlines(),1) if 555<=i<=575))
# passes rewrite at 25d6b82: show removed lines count/sample
d=git("show","25d6b82","--","docs/metrics/passes.jsonl")
rem=[l for l in d.splitlines() if l.startswith("-") and not l.startswith("---")]
add=[l for l in d.splitlines() if l.startswith("+") and not l.startswith("+++")]
print(f"\n25d6b82 passes.jsonl removed={len(rem)} added={len(add)}")
for l in rem[:4]: print("  -",l[:200])
for l in add[:4]: print("  +",l[:200])
d2=git("show","25d6b82","--","docs/metrics/briefs.jsonl")
print("25d6b82 briefs removed:",[l[:160] for l in d2.splitlines() if l.startswith("-") and not l.startswith("---")][:3])
