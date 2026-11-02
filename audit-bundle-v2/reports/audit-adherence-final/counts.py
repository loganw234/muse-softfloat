# counts.py — auditor-adherence-final census (Git Bash, MSF_PYTHON pinned to workspace .venv)
# Reproduces the headline counts cited in report.md at muse-softfloat HEAD.
# Usage: MSF_PYTHON=.venv/Scripts/python.exe; "$MSF_PYTHON" scratch/audit-adherence-final/counts.py
import json, subprocess, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parents[2]
MSF = ROOT / "muse-softfloat"
def git(*a):
    return subprocess.run(["git", "-C", str(MSF)] + list(a), capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout
def body(h):
    return subprocess.run(["git", "-C", str(MSF), "log", "-1", "--format=%B", h],
                          capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
allh = [l for l in git("log", "--format=%H").splitlines() if l.strip()]
print("commits", len(allh))
noco = [h for h in allh if "Co-Authored-By" not in body(h)]
print("missing-trailer", len(noco), noco[:5])
fp = [l for l in git("log", "--first-parent", "--format=%H").splitlines() if l.strip()]
print("first-parent", len(fp))
print("first-parent-no-ledger-ref", sum(1 for h in fp if "ledger" not in body(h).lower()))
m = MSF / "docs" / "metrics"
for f in ["passes.jsonl", "usage.jsonl", "plants.jsonl", "escalations.jsonl",
          "corrections.jsonl", "briefs.jsonl", "fetches.jsonl"]:
    rows = [json.loads(l) for l in (m / f).open(encoding="utf-8") if l.strip()]
    print(f, len(rows))
pl = [json.loads(l) for l in (m / "plants.jsonl").open(encoding="utf-8") if l.strip()]
print("plants grade:", collections.Counter(r.get("grade") for r in pl))
print("plants checked_by:", collections.Counter(r.get("checked_by") for r in pl))
print("plants distinct key_sha256:", len(set(r.get("key_sha256") for r in pl)))
pa = [json.loads(l) for l in (m / "passes.jsonl").open(encoding="utf-8") if l.strip()]
print("passes sent_back:", collections.Counter(r.get("sent_back") for r in pa))
br = [json.loads(l) for l in (m / "briefs.jsonl").open(encoding="utf-8") if l.strip()]
print("briefs time_box_min:", collections.Counter(r.get("time_box_min") for r in br))
print("briefs ceiling_lines==0:", sum(1 for r in br if r.get("ceiling_lines") == 0))
