"""Check copy objects exist; dump usage schema + plant rows for seal verifiers.
Run: MSF_PYTHON objects.py
"""
import json, subprocess, os

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "muse-softfloat")

def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                          capture_output=True, text=True).stdout.strip()

for h in ["fa8a27a", "2221ace", "3cec27c", "4bed622", "549832e",
          "ee0c8b9", "a1e83d9", "8507695", "c537e0d", "fe04000"]:
    t = git("cat-file", "-t", h)
    print(f"{h}: {t or 'MISSING'}")

print("\n=== usage row keys ===")
with open(os.path.join(REPO, "docs", "metrics", "usage.jsonl"), encoding="utf-8") as f:
    first = json.loads(f.readline())
print(sorted(first.keys()))
print(json.dumps(first, indent=None)[:600])

print("\n=== seal verifier usage rows ===")
with open(os.path.join(REPO, "docs", "metrics", "usage.jsonl"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        a = r.get("agent", "")
        if a.startswith("verifier-w6") or a == "verifier-polish1":
            print(json.dumps(r)[:500])

print("\n=== plants rows for seal copies (grade + at) ===")
with open(os.path.join(REPO, "docs", "metrics", "plants.jsonl"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        print(sorted(r.keys()))
        break
with open(os.path.join(REPO, "docs", "metrics", "plants.jsonl"), encoding="utf-8") as f:
    n = 0
    for line in f:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        v = r.get("verifier", r.get("checked_by", "?"))
        if isinstance(v, str) and ("w6" in v or "polish1" in v):
            n += 1
            if n <= 50:
                print(json.dumps(r)[:400])
    print(f"seal plant rows printed: {n}")
