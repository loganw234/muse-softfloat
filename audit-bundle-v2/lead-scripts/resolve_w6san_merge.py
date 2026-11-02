import json
import pathlib
import subprocess

repo = pathlib.Path("muse-softfloat")

# ci.yml: single hunk, both sides are additive jobs -> keep both in order
p = repo / ".github/workflows/ci.yml"
text = p.read_text(encoding="utf-8")
assert text.count("<<<<<<< HEAD") == 1 and text.count(">>>>>>> wave6-sanitize") == 1
lines = [x for x in text.split("\n")
         if not x.startswith(("<<<<<<<", "=======", ">>>>>>>"))]
out = "\n".join(lines)
for job in ("smoke:", "standard:", "example-host:", "sanitize:"):
    assert out.count("\n  " + job) == 1, (job, out.count("\n  " + job))
p.write_bytes(out.encode("utf-8"))
print("ci.yml resolved: 4 jobs present once each")

# briefs.jsonl: ours bytes + theirs' new row appended
ours = subprocess.check_output(["git", "-C", str(repo), "show", ":2:docs/metrics/briefs.jsonl"])
theirs = subprocess.check_output(["git", "-C", str(repo), "show", ":3:docs/metrics/briefs.jsonl"])
trows = [x for x in theirs.decode("utf-8").splitlines() if x.strip()]
san = [x for x in trows if json.loads(x).get("author") == "parcel-w6sanitize"]
assert len(san) == 1, san
joined = ours if ours.endswith(b"\n") else ours + b"\n"
joined += (san[0] + "\n").encode("utf-8")
rows = [json.loads(x) for x in joined.decode("utf-8").splitlines() if x.strip()]
print("briefs rows:", len(rows), "last three:", [r["author"] for r in rows[-3:]])
assert len(rows) == 36, len(rows)
(repo / "docs/metrics/briefs.jsonl").write_bytes(joined)
