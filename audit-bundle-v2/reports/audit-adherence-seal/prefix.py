"""Append-only check: every metrics file at HEAD must start with the exact
bc807e6 bytes (frozen prefix byte-identical), only appended rows after.
Also RECORD.md deletion scan and diffstat of the span.
Run: MSF_PYTHON prefix.py
"""
import subprocess, os

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "muse-softfloat")
BASE = "bc807e6"
HEAD = "751d1d6"
FILES = ["docs/metrics/passes.jsonl", "docs/metrics/plants.jsonl",
         "docs/metrics/usage.jsonl", "docs/metrics/briefs.jsonl",
         "docs/metrics/escalations.jsonl", "docs/metrics/corrections.jsonl",
         "docs/RECORD.md"]

def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                           capture_output=True, text=True).stdout

def show(path):
    return subprocess.run(["git", "-C", REPO, "show", f"{HEAD}:{path}"],
                           capture_output=True).stdout

def showbase(path):
    return subprocess.run(["git", "-C", REPO, "show", f"{BASE}:{path}"],
                           capture_output=True).stdout

for f in FILES:
    old, new = showbase(f), show(f)
    is_prefix = new.startswith(old)
    print(f"{f}: base={len(old)} head={len(new)} prefix_intact={is_prefix} "
          f"appended_bytes={len(new)-len(old) if is_prefix else 'N/A'}")
    if not is_prefix:
        # find first divergence
        n = min(len(old), len(new))
        i = next((k for k in range(n) if old[k:k+1] != new[k:k+1]), n)
        print(f"  FIRST DIVERGENCE at byte {i}: base={old[max(0,i-60):i+60]!r}")
        print(f"                              head={new[max(0,i-60):i+60]!r}")

print("\n=== diffstat docs/ + video/ over span ===")
print(git("diff", "--stat", f"{BASE}", HEAD, "--", "docs/", "video/")[:3000])
print("\n=== numstat for metrics files ===")
print(git("diff", "--numstat", f"{BASE}", HEAD, "--", "docs/metrics/"))
