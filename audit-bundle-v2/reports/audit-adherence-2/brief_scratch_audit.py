#!/usr/bin/env python3
"""Brief-shape checks + scratch report inventory. Read-only. Skips cft names. Keys: hash only."""
import os, re, hashlib
def skip(n): return "cft" in n.lower()
CHECKS={
 "time_box": r"time box|time-box|\b\d+\s*min(ute)?s?\b.*box|box.*\b\d+\s*min",
 "ceiling": r"ceiling|scope ceiling|lines\b.*max|max.*lines",
 "own_files": r"own|owned files|files you own|your files",
 "forbidden": r"forbidden|must not|never (touch|edit|modify)|do not (touch|edit|modify)|off[- ]limits",
 "neg_control": r"negative control",
 "READY_def": r"READY means|READY =|what READY|READY:",
 "brief_wrong": r"brief (got|has) wrong|brief-got-wrong|what this brief got wrong|brief was wrong",
 "design_first": r"design (first|entry|before)|design:.*ledger|write.*design.*ledger",
 "clean_room": r"clean.room|cft|never open.*search",
 "ledger_rule": r"ledger\.sh|Measured|append.only|three read|read moments",
 "script_files": r"script files|Git Bash|MSF_PYTHON",
 "base_commit": r"base|at or after|branched from|cut from",
 "escalation_test": r"test escalation|urgent/",
 "not_do": r"what you did not do|not done|did not do|skipped",
}
print("== brief shape (ledger/briefs/*.md)")
for fn in sorted(os.listdir("ledger/briefs")):
    if skip(fn) or not fn.endswith(".md"): continue
    t=open(os.path.join("ledger/briefs",fn),encoding="utf-8",errors="replace").read()
    res={k: bool(re.search(v,t,re.I)) for k,v in CHECKS.items()}
    miss=[k for k,v in res.items() if not v]
    print(f"  {fn} ({len(t)}b) missing: {miss}")
print("\n== scratch report inventory (report.md first verdict-ish lines)")
for d in sorted(os.listdir("scratch")):
    if skip(d): continue
    rp=os.path.join("scratch",d,"report.md")
    if os.path.isfile(rp):
        t=open(rp,encoding="utf-8",errors="replace").read()
        first=[l for l in t.splitlines() if l.strip()][:2]
        verd=re.findall(r"\b(NOT READY|READY|PASS|FAIL|REFUS\w*|ADHERENT\w*|NON-ADHERENT)\b",t)
        from collections import Counter
        print(f"  scratch/{d}/report.md ({len(t)}b) verdict-tokens={dict(Counter(verd))} first={first[0][:110] if first else ''}")
    else:
        print(f"  scratch/{d}/ NO report.md; files={sorted(os.listdir(os.path.join('scratch',d)))[:8] if os.path.isdir(os.path.join('scratch',d)) else 'file'}")
print("\n== lead keys: names + sha256 only (contents NOT opened)")
kd="scratch/lead/keys"
if os.path.isdir(kd):
    for fn in sorted(os.listdir(kd)):
        p=os.path.join(kd,fn)
        h=hashlib.sha256(open(p,'rb').read()).hexdigest()
        print(f"  {fn} sha256={h} bytes={os.path.getsize(p)}")
else: print("  no scratch/lead/keys dir; scratch/lead entries:", sorted(os.listdir("scratch/lead"))[:30] if os.path.isdir("scratch/lead") else "ABSENT")
print("\n== scratch/lead top-level names (names only):")
if os.path.isdir("scratch/lead"): print("  ", sorted(os.listdir("scratch/lead")))
print("\n== planted copies: look for copy dirs under scratch (names matching copy/plant, depth<=2)")
for d in sorted(os.listdir("scratch")):
    if skip(d): continue
    base=os.path.join("scratch",d)
    if not os.path.isdir(base): continue
    for sub in sorted(os.listdir(base)):
        if skip(sub): continue
        if re.search(r"copy|plant",sub,re.I):
            print(f"  scratch/{d}/{sub} isdir={os.path.isdir(os.path.join(base,sub))}")
