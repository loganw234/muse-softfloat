#!/usr/bin/env python3
"""Merge/verifier chronology + lead heading list + report mtimes. Read-only."""
import os, re, sys, subprocess
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO="muse-softfloat"; SAFE="C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat"
def git(*a):
    return subprocess.run(["git","-C",REPO,"-c",f"safe.directory={SAFE}",*a],capture_output=True,text=True,encoding="utf-8",errors="replace").stdout
HEAD=re.compile(r"^## (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{2}:?\d{2}) - (.*)$",re.M)
def parse(s):
    for f in ("%Y-%m-%d %H:%M:%S %z",):
        try: return datetime.strptime(s,f)
        except Exception: pass
    return None
print("== lead.md headings (all)")
t=open("ledger/lead.md",encoding="utf-8",errors="replace").read()
for m in HEAD.finditer(t): print(f"  {m.group(1)} :: {m.group(2)[:130]}")
print("\n== unstamped ledger files (0 stamped headings): mtime + first lines")
for fn in sorted(os.listdir("ledger")):
    if not fn.endswith(".md") or fn=="README.md": continue
    p=os.path.join("ledger",fn); tx=open(p,encoding="utf-8",errors="replace").read()
    if not HEAD.search(tx):
        mt=datetime.fromtimestamp(os.path.getmtime(p)).isoformat()
        fl=[l for l in tx.splitlines() if l.strip()][:1]
        print(f"  {fn}: mtime={mt} bytes={len(tx)} first={fl[0][:110] if fl else ''}")
print("\n== verifier/parcel ledger last stamped entry (or mtime) vs merge times")
merges=[]
raw=git("log","--first-parent","--merges","main","--format=%h%x1f%ci%x1f%s")
for line in raw.splitlines():
    h,d,s=line.split("\x1f"); merges.append((h,d,s))
for h,d,s in reversed(merges): print(f"  MERGE {h} {d} {s[:100]}")
print("\n== scratch report.md mtimes")
for dname in sorted(os.listdir("scratch")):
    rp=os.path.join("scratch",dname,"report.md")
    if os.path.isfile(rp):
        print(f"  {dname}: mtime={datetime.fromtimestamp(os.path.getmtime(rp)).isoformat()}")
print("\n== merge bodies (full) ")
for h,d,s in reversed(merges):
    body=git("log","-1","--format=%b",h)
    print(f"\n--- MERGE {h} {d} {s}\n{body.strip()[:2600]}")
