"""Resolve: worktree object presence; full sent_back=true rows; briefs counts
per parent; history.json merge fields."""
import json, subprocess, os

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "muse-softfloat")
WS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")

def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                          capture_output=True, text=True)

print("object presence via worktree gitdir:")
for d in ["worktrees/verify-polish1", "worktrees/verify6-augint", "worktrees/verify6-popups"]:
    p = os.path.join(WS, d)
    r = subprocess.run(["git", "-C", p, "cat-file", "-t", "HEAD"], capture_output=True, text=True)
    print(f"  {d}: {r.stdout.strip() or 'ERR: ' + r.stderr.strip()[:150]}")
    r2 = subprocess.run(["git", "-C", p, "status"], capture_output=True, text=True)
    print(f"    status rc={r2.returncode} out={r2.stdout.strip()[:80]} err={r2.stderr.strip()[:120]}")

print("\nfull sent_back=true rows (wave6/polish):")
with open(os.path.join(REPO, "docs", "metrics", "passes.jsonl"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("sent_back") is True and r.get("wave") in ("wave6", "polish"):
            print(json.dumps(r))

print("\nbriefs nonempty rows:")
for rev in ["cdc40ae", "5b9fff3", "e7087dc", "47f5ea7", "751d1d6", "bc807e6"]:
    out = git("show", f"{rev}:docs/metrics/briefs.jsonl").stdout
    n = len([l for l in out.split("\n") if l.strip()])
    print(f"  {rev}: {n}")

print("\nhistory.json merge fields:")
with open(os.path.join(REPO, "video", "segments", "history.json"), encoding="utf-8") as f:
    h = json.load(f)
for k in ("extracted_from", "head_main", "head_short", "commit_count_all",
          "main_first_parent_count", "merge_count", "merges_into_main", "branch_count"):
    print(f"  {k}={h.get(k)}")
print("process_graph sources:", end=" ")
with open(os.path.join(REPO, "video", "segments", "process_graph.json"), encoding="utf-8") as f:
    g = json.load(f)
print(json.dumps(g.get("sources"))[:500])
print("accounting:", json.dumps(g.get("accounting"))[:500])
