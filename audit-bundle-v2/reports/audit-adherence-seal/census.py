"""Census of the seal span bc807e6..751d1d6: trailers, ledger refs, merge bodies.
Run: MSF_PYTHON census.py  (MSF_PYTHON = workspace .venv python)
Read-only: only git show/log commands against muse-softfloat.
"""
import subprocess, sys, os

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "muse-softfloat")
BASE = "bc807e6"
HEAD = "751d1d6"

def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                           capture_output=True, text=True).stdout

commits = git("log", "--format=%H", f"{BASE}..{HEAD}").split()
print(f"span commits: {len(commits)} (base {BASE}, head {HEAD})")
fp = git("log", "--format=%H", "--first-parent", f"{BASE}..{HEAD}").split()
print(f"first-parent: {len(fp)}")

no_trailer, no_ledger = [], []
for h in commits:
    body = git("log", "-1", "--format=%B", h)
    subj = body.splitlines()[0] if body.splitlines() else ""
    if "Co-Authored-By:" not in body:
        no_trailer.append((h[:7], subj))
    if "ledger" not in body.lower():
        no_ledger.append((h[:7], subj))

print(f"\nno Co-Authored-By trailer: {len(no_trailer)}/{len(commits)}")
for h, s in no_trailer:
    print(f"  {h} {s}")
print(f"\nno 'ledger' ref in body: {len(no_ledger)}/{len(commits)}")
for h, s in no_ledger:
    print(f"  {h} {s}")

print("\n=== merge bodies (first-parent merges) ===")
merges = git("log", "--format=%H %s", "--first-parent", "--merges",
             f"{BASE}..{HEAD}").splitlines()
for line in merges:
    h = line.split()[0]
    body = git("log", "-1", "--format=%B", h)
    lines = [l for l in body.splitlines()[1:] if l.strip()]
    print(f"--- {line}")
    for l in lines[:12]:
        print(f"    {l}")
