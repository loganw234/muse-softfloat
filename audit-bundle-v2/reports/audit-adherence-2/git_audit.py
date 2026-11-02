#!/usr/bin/env python3
"""Count git-history adherence facts for muse-softfloat. Read-only."""
import subprocess, sys, re, json
REPO = "muse-softfloat"
SAFE = "C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat"
def git(*args):
    r = subprocess.run(["git","-C",REPO,"-c",f"safe.directory={SAFE}",*args],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout
def main():
    out = []
    # all commits reachable from main
    fmt = "%H%x1f%P%x1f%ci%x1f%an%x1f%s%x1f%b%x1e"
    raw = git("log","main",f"--format={fmt}")
    commits = []
    for rec in raw.split("\x1e"):
        rec = rec.strip("\n")
        if not rec.strip(): continue
        parts = rec.split("\x1f")
        if len(parts) < 6: continue
        h, parents, date, author, subj, body = parts[:6]
        commits.append(dict(h=h, parents=parents.split() if parents else [],
                            date=date, author=author, subj=subj, body=body))
    out.append(f"commits reachable from main: {len(commits)}")
    merges = [c for c in commits if len(c["parents"])>1]
    out.append(f"merge commits: {len(merges)}")
    cab = [c for c in commits if "Co-Authored-By:" in (c["body"])]
    out.append(f"with Co-Authored-By trailer: {len(cab)}/{len(commits)}")
    nocab = [c for c in commits if "Co-Authored-By:" not in c["body"]]
    for c in nocab:
        out.append(f"  NO-CAB {c['h'][:7]} {c['date']} {c['subj'][:80]}")
    nobody = [c for c in commits if len(c["body"].strip()) < 40]
    out.append(f"body <40 chars (incl trailer-only): {len(nobody)}")
    for c in nobody:
        out.append(f"  SHORT-BODY {c['h'][:7]} len={len(c['body'].strip())} {c['subj'][:80]}")
    bodylens = sorted(len(c["body"].strip()) for c in commits)
    out.append(f"body chars min/med/max: {bodylens[0]}/{bodylens[len(bodylens)//2]}/{bodylens[-1]}")
    # first-parent chain
    fp_raw = git("log","--first-parent","main",f"--format={fmt}")
    fp = []
    for rec in fp_raw.split("\x1e"):
        rec = rec.strip("\n")
        if not rec.strip(): continue
        p = rec.split("\x1f")
        if len(p) < 6: continue
        fp.append(dict(h=p[0], parents=p[1].split() if p[1] else [], date=p[2], subj=p[4], body=p[5]))
    out.append(f"\nfirst-parent main chain: {len(fp)} commits (newest first)")
    for c in fp:
        kind = "MERGE" if len(c["parents"])>1 else "lead? "
        refs = []
        b = c["body"].lower()
        for w in ("verifier","ready","ledger","plant","recheck","audit","standard","smoke","board"):
            if w in b: refs.append(w)
        out.append(f"  {kind} {c['h'][:7]} {c['date']} cab={'Co-Authored-By:' in c['body']} refs={','.join(refs)} :: {c['subj'][:100]}")
    # remote comparison
    out.append("\nremote/local:")
    out.append(git("rev-parse","main","origin/main").strip().replace("\n"," vs "))
    # branches and whether merged into main
    out.append("\nbranches:")
    br = git("branch","--format=%(refname:short)").splitlines()
    merged = set(x.strip(" *+") for x in git("branch","--merged","main").splitlines())
    for bname in br:
        bname=bname.strip(" *+")
        tip = git("log","-1","--format=%h %ci %s", bname).strip()
        out.append(f"  {bname}: merged_into_main={bname in merged} tip={tip[:110]}")
    # authors
    from collections import Counter
    out.append("\nauthors: " + repr(Counter(c["author"] for c in commits)))
    # which commits touch metrics/RECORD relative timing: list commits touching docs/RECORD.md and metrics
    for path in ("docs/RECORD.md","docs/metrics/plants.jsonl","docs/metrics/passes.jsonl","docs/metrics/briefs.jsonl"):
        lst = git("log","--format=%h %ci %s","main","--",path).splitlines()
        out.append(f"\ncommits touching {path}: {len(lst)}")
        for l in lst[:30]: out.append("  "+l[:120])
    print("\n".join(out))
if __name__ == "__main__":
    main()
