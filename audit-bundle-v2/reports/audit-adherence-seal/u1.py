"""U1 resolution: w5demo plant shapes vs report findings; demo HEAD state;
w6popups passes timestamps; plants.jsonl fence in w6 verifier briefs."""
import json, subprocess, os

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "muse-softfloat")
WS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")

print("w5demo plants rows:")
with open(os.path.join(REPO, "docs", "metrics", "plants.jsonl"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("verifier") == "verifier-w5demo":
            print(f"  plant {r['plant']} grade={r['grade']} shape={r['shape'][:110]}")

def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                          capture_output=True, text=True).stdout

print("\nHEAD demo/fetch.py 'if False':")
out = git("grep", "-n", "if False", "HEAD", "--", "demo/fetch.py")
print("  " + (out.strip() or "ABSENT at HEAD"))
print("HEAD run_demo host_ok/|| true:")
out = git("grep", "-n", "host_ok", "HEAD", "--", "demo/run_demo.sh")
print("  " + (out.strip()[:300] or "ABSENT"))
out = git("grep", "-n", "cache2", "HEAD", "--", "demo/.gitignore", ".gitignore")
print("  cache2 ref: " + (out.strip()[:200] or "ABSENT"))

print("\nw6popups passes row:")
with open(os.path.join(REPO, "docs", "metrics", "passes.jsonl"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("agent") == "verifier-w6popups":
            print("  " + json.dumps(r))

print("\nplants.jsonl fence in w6 verifier briefs:")
import glob
for p in sorted(glob.glob(os.path.join(WS, "ledger", "briefs", "verify-w6*.md")) +
                glob.glob(os.path.join(WS, "ledger", "briefs", "verify-polish1.md"))):
    with open(p, encoding="utf-8") as f:
        t = f.read()
    has = "plants.jsonl" in t
    print(f"  {os.path.basename(p)}: mentions plants.jsonl={has}")
