"""Probe1c: merges_into_main from history.json; run.sh composition; RECORD."""
import json, sys, re
from pathlib import Path
from collections import Counter
DUP = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
hist = json.load(open(DUP / "video/segments/history.json", encoding="utf-8"))
print("merge_count:", hist.get("merge_count"))
print("merges_into_main:", hist.get("merges_into_main"))
print("branch_count:", hist.get("branch_count"))
merges = hist["merges"]
print("targets:", Counter(m.get("target") for m in merges))
print("target_branch:", Counter(m.get("target_branch") for m in merges))
nonmain = [(m["short"], m.get("target"), m.get("target_branch"), m.get("subject")) for m in merges if m.get("target") != "main" and m.get("target_branch") != "main"]
print("non-main merges:", nonmain)
mainm = [m for m in merges if m.get("target") == "main" or m.get("target_branch") == "main"]
print("main-target merges:", len(mainm))

print("=== run.sh ===")
run = (DUP / "tools/run.sh").read_text(encoding="utf-8")
print("run.sh bytes:", len(run))
# find budget/RECORD/total lines
for i, l in enumerate(run.splitlines()):
    if re.search(r"RECORD|budget|BUDGET|total|TOTAL|smoke|standard|aug", l, re.I):
        print(f"{i+1}: {l}")
