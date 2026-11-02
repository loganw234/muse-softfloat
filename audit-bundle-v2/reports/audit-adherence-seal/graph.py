"""Graph-lane counts vs film card; worktree HEADs; sent_back=true rows;
briefs rows at the metrics merge."""
import json, subprocess, os

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "muse-softfloat")
WS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")

def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                          capture_output=True, text=True).stdout.strip()

for name in ["video/segments/process_graph.json", "video/segments/history.json"]:
    p = os.path.join(REPO, name)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        print(f"{name}: type={type(d).__name__} ", end="")
        if isinstance(d, dict):
            print(f"keys={list(d.keys())[:10]}")
            for k in ("freeze", "frozen", "base", "commit", "generated", "at", "note"):
                if k in d:
                    print(f"  {k}={str(d[k])[:200]}")
        elif isinstance(d, list):
            print(f"len={len(d)}")
    else:
        print(f"{name}: ABSENT")

with open(os.path.join(REPO, "video", "segments", "process_graph.json"), encoding="utf-8") as f:
    g = json.load(f)
# find episode list wherever it lives
def walk(o, depth=0):
    if depth > 3:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                roles = {}
                for e in v:
                    r = e.get("role", "?")
                    roles[r] = roles.get(r, 0) + 1
                print(f"list at [{k}]: n={len(v)} roles={roles}")
            walk(v, depth + 1)
walk(g)

print("\nworktree HEADs:")
for d in ["worktrees/verify-polish1", "worktrees/verify6-augint", "worktrees/verify6-ci",
          "worktrees/verify6-popups", "worktrees/verify6-filmretime"]:
    p = os.path.join(WS, d)
    try:
        r = subprocess.run(["git", "-C", p, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        s = subprocess.run(["git", "-C", p, "status", "--short"], capture_output=True, text=True).stdout.strip()
        print(f"  {d}: HEAD={r[:9] if r else 'ERR:'+r} clean={not bool(s)}")
    except Exception as e:
        print(f"  {d}: {e}")

print("\npasses rows with sent_back=true (wave6/polish):")
with open(os.path.join(REPO, "docs", "metrics", "passes.jsonl"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("sent_back") is True and r.get("wave") in ("wave6", "polish"):
            print(f"  {r.get('agent')} work={str(r.get('work'))[:80]}")

print("\nbriefs rows at 47f5ea7:")
out = git("show", "47f5ea7:docs/metrics/briefs.jsonl")
rows = [l for l in out.split("\n") if l.strip()]
print(f"  nonempty rows={len(rows)}")
print("briefs rows at HEAD with wave6/polish/auditor:")
out2 = git("show", "HEAD:docs/metrics/briefs.jsonl")
for l in out2.split("\n"):
    if l.strip():
        try:
            r = json.loads(l)
            if r.get("wave") in ("wave6", "polish") or "audit" in r.get("author", ""):
                print(f"  {r.get('wave')}/{r.get('author')}")
        except Exception:
            pass
