"""Follow-ups: briefs non-empty rows; wave6 passes sent_back; merge count at
a73e97d freeze; worktree copies present; w5site residue in site/data.json.
Run: MSF_PYTHON followups.py
"""
import json, subprocess, os

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "muse-softfloat")
WS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")

def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                          capture_output=True, text=True).stdout.strip()

with open(os.path.join(REPO, "docs", "metrics", "briefs.jsonl"), encoding="utf-8") as f:
    lines = f.read().split("\n")
nonempty = [l for l in lines if l.strip()]
print(f"briefs lines={len(lines)} nonempty={len(nonempty)}")

print("\npasses rows by wave with sent_back:")
from collections import Counter
with open(os.path.join(REPO, "docs", "metrics", "passes.jsonl"), encoding="utf-8") as f:
    for line in f:
        pass
rows = [json.loads(l) for l in open(os.path.join(REPO, "docs", "metrics", "passes.jsonl"), encoding="utf-8") if l.strip()]
c = Counter((r.get("wave"), r.get("sent_back", "<MISSING>")) for r in rows)
for k in sorted(c, key=str):
    print(f"  {k}: {c[k]}")

print("\nfirst-parent merges at a73e97d:", len(git("log", "--format=%h", "--first-parent", "--merges", "a73e97d").split()))
print("first-parent merges at 97e10a4 (judgemap landing):", len(git("log", "--format=%h", "--first-parent", "--merges", "97e10a4").split()))
print("first-parent merges at f01dc96 (popups base):", len(git("log", "--format=%h", "--first-parent", "--merges", "f01dc96").split()))

print("\nprocess_graph.json history:")
print(git("log", "--format=%h %ci %s", "--", "video/segments/process_graph.json"))
print(git("log", "--format=%h %ci %s", "--", "video/segments/history.json"))

print("\nworktree copies present:")
for d in ["worktrees/verify-polish1", "worktrees/verify6-augint", "worktrees/verify6-ci",
          "worktrees/verify6-examples", "worktrees/verify6-sanitize", "worktrees/verify6-judgemap",
          "worktrees/verify6-filmretime", "worktrees/verify6-popups", "worktrees/verify6-captions",
          "worktrees/verify6-metrics", "worktrees/dup-v6popups"]:
    p = os.path.join(WS, d)
    print(f"  {d}: {'PRESENT' if os.path.isdir(p) else 'absent'}")

print("\nsite/data.json plant figures:")
with open(os.path.join(REPO, "site", "data.json"), encoding="utf-8") as f:
    d = json.load(f)
print(json.dumps(d, indent=None)[:800])
