"""Derive every popup-card project total by script (no invented numbers)."""
import json
import subprocess
from collections import Counter

SEG = "worktrees/w6-popups/video/segments"
MET = "worktrees/w6-popups/docs/metrics"

pg = json.load(open(SEG + "/process_graph.json", encoding="utf-8"))
hist = json.load(open(SEG + "/history.json", encoding="utf-8"))
acc = pg["accounting"]
lanes = [e for e in pg["episodes"] if e["kind"] == "lane"]

print("== frozen graph (replay draws this) ==")
print("lane_episodes", acc["lane_episodes"])
print("by_role", json.dumps(acc["by_role"]))
print("by_passes_role", json.dumps(acc["by_passes_role"]))
print("plants_rows", acc["plants_rows"], "mapped", acc["plants_rows_mapped"],
      "unmapped", acc["plants_rows_unmapped"])
print("plants_verifiers", acc["plants_verifiers"],
      "mapped", acc["plants_verifiers_mapped"])
ticks = [t for e in lanes for t in (e.get("plants") or [])]
print("ticks drawn", len(ticks),
      "caught", sum(1 for t in ticks if t["grade"] == "caught"),
      "missed", sum(1 for t in ticks if t["grade"] != "caught"))
print("merges_into_main", acc["git_merges_into_main"],
      "owned_by_author", len(acc["git_merges_owned_by_author_episode"]),
      "lead_only", len(acc["git_merges_lead_only_no_episode"]))
print("history merge_count", hist["merge_count"],
      "merges_into_main", hist["merges_into_main"],
      "commit_count_all", hist["commit_count_all"])
spine = [e for e in pg["episodes"] if e["kind"] == "spine"]
print("spine", [(e["agent"], e["role"], e["passes_role"]) for e in spine])

print("== HEAD docs/metrics ==")


def rows(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


passes = rows(MET + "/passes.jsonl")
print("passes", len(passes), dict(Counter(r["role"] for r in passes)))
briefs = rows(MET + "/briefs.jsonl")
print("briefs", len(briefs))
esc = rows(MET + "/escalations.jsonl")
print("escalations", len(esc))
with open(MET + "/plants.jsonl", encoding="utf-8") as f:
    plants = [line for line in f if line.strip()]
print("plants HEAD lines", len(plants))

print("== HEAD committed-vector count (same files as run.sh VECS) ==")
out = subprocess.run(
    ["C:/Program Files/Git/bin/bash.exe", "-lc",
     "cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-popups"
     " && awk '!/^#/ && NF>0' tests/vectors/*.vec | wc -l"],
    capture_output=True, text=True)
print("committed vector lines:", out.stdout.strip(), out.stderr.strip())
