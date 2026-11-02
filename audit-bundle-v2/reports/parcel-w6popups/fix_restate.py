"""Restate the parcel-w6popups briefs.jsonl row in place (no append)."""
import json

P = r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-popups\docs\metrics\briefs.jsonl"
with open(P, encoding="utf-8") as f:
    lines = f.read().splitlines()
print("rows before:", len(lines))
row = json.loads(lines[-1])
assert row["author"] == "parcel-w6popups" and row["wave"] == "wave6", row
old = row["work"]
row["work"] = old.replace(
    "(20 parcels, 3 escalations,",
    "(19 parcels, 20 escalation filings with 3 fixes,",
)
assert row["work"] != old
lines[-1] = json.dumps(row, ensure_ascii=False)
with open(P, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(lines) + "\n")
with open(P, encoding="utf-8") as f:
    check = f.read().splitlines()
print("rows after:", len(check))
print(check[-1][:400])
