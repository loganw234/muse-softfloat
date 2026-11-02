#!/usr/bin/env python3
"""Claims, coverage, tree/clean-room samples. Read-only. Skips any name containing cft."""
import os, re, csv, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from collections import Counter

def skip(name): return "cft" in name.lower()

# COVERAGE.tsv status counts
p="muse-softfloat/docs/COVERAGE.tsv"
with open(p,encoding="utf-8",errors="replace") as f:
    rows=list(csv.reader(f,delimiter="\t"))
print("COVERAGE header:", rows[0])
print("COVERAGE rows:", len(rows)-1)
# count each column's distinct values for short columns
for ci,h in enumerate(rows[0]):
    vals=Counter(r[ci] for r in rows[1:] if len(r)>ci)
    if len(vals)<=25: print(f" col[{ci}] {h}: {dict(vals)}")
print(" unconfirmed cells total:", sum(r.count("unconfirmed") for r in rows[1:]))

# performance / timing words in claim files
perf=re.compile(r"\b(fast(?:er|est)?|speedup|performance|benchmark|cycles?|MHz|ns\b|µs|throughput|latency)\b", re.I)
for path in ("muse-softfloat/README.md","muse-softfloat/docs/RECORD.md","muse-softfloat/docs/BOARD.md","muse-softfloat/AGENTS.md"):
    print(f"\n== perf/timing lines in {path}")
    for i,line in enumerate(open(path,encoding="utf-8",errors="replace"),1):
        if perf.search(line): print(f"  {path}:{i}: {line.strip()[:200]}")

# claim tokens / deferred
for path in ("muse-softfloat/docs/studies/SF-0.md","muse-softfloat/docs/studies/SF-1.md","muse-softfloat/docs/studies/SF-2.md"):
    t=open(path,encoding="utf-8",errors="replace").read()
    print(f"\n== {path}: defer*={len(re.findall(r'defer',t,re.I))} claim={len(re.findall(r'claim',t,re.I))} headings:")
    for m in re.finditer(r"^(#{1,3} .*)$",t,re.M): print("   ",m.group(1)[:110])

# RECORD structure
t=open("muse-softfloat/docs/RECORD.md",encoding="utf-8",errors="replace").read()
print("\n== RECORD headings:")
for m in re.finditer(r"^(#{1,3} .*)$",t,re.M): print("   ",m.group(1)[:120])

# tree sample: third-party markers in src/include/tests/tools/board (names only + marker counts)
print("\n== repo tree file counts by top dir + third-party markers")
markers=("Berkeley","SoftFloat","TestFloat","MPFR","Copyright (c)","SPDX","kissfft","KISS FFT","REBOUND","IAS15")
counts=Counter(); markerhits=[]
for root,dirs,files in os.walk("muse-softfloat"):
    dirs[:]=[d for d in dirs if d not in (".git",) and not skip(d)]
    for fn in files:
        if skip(fn): continue
        rel=os.path.join(root,fn).replace("\\","/")
        top=rel.split("/")[1] if "/" in rel[len("muse-softfloat/"):] else "(root)"
        counts[top]+=1
        if fn.endswith((".c",".h",".py",".sh",".md",".txt",".cmake")) or fn=="CMakeLists.txt":
            try: txt=open(os.path.join(root,fn),encoding="utf-8",errors="replace").read()
            except Exception: continue
            for mk in markers:
                n=txt.count(mk)
                if n: markerhits.append((rel,mk,n))
print(dict(counts))
for h in markerhits: print("  MARKER",h)
# LICENSE files
print("\n== licence-ish files:")
for root,dirs,files in os.walk("muse-softfloat"):
    dirs[:]=[d for d in dirs if d!=".git" and not skip(d)]
    for fn in files:
        if re.search(r"licen[cs]e|notice|copying",fn,re.I) and not skip(fn):
            print("  ",os.path.join(root,fn).replace("\\","/"))
# run.sh inventory/controls markers
print("\n== tools listing:")
for fn in sorted(os.listdir("muse-softfloat/tools")): print("  ",fn, os.path.getsize(os.path.join("muse-softfloat/tools",fn)))
t=open("muse-softfloat/tools/run.sh",encoding="utf-8",errors="replace").read()
for i,line in enumerate(t.splitlines(),1):
    if re.search(r"control|inventory|INVENTORY|board\.lock|serial|picotool|MSF_PYTHON|refus",line,re.I):
        print(f"  run.sh:{i}: {line.strip()[:180]}")
