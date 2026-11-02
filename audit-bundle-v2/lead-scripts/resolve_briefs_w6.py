import json
import subprocess

repo = "muse-softfloat"
ours = subprocess.check_output(["git", "-C", repo, "show", ":2:docs/metrics/briefs.jsonl"])
theirs = subprocess.check_output(["git", "-C", repo, "show", ":3:docs/metrics/briefs.jsonl"])
base = subprocess.check_output(["git", "-C", repo, "show", "50aac59:docs/metrics/briefs.jsonl"])
assert ours.startswith(base) or base.endswith(b"\n"), "ours not base-prefixed"
their_rows = [x for x in theirs.decode("utf-8").splitlines() if x.strip()]
ci_row = [x for x in their_rows if json.loads(x).get("author") == "parcel-w6ci"]
assert len(ci_row) == 1, ci_row
out = ours
if not out.endswith(b"\n"):
    out += b"\n"
out += (ci_row[0] + "\n").encode("utf-8")
rows = [json.loads(x) for x in out.decode("utf-8").splitlines() if x.strip()]
authors = [r["author"] for r in rows]
print("rows:", len(rows), "last two authors:", authors[-2:])
assert len(rows) == 34, len(rows)
open(repo + "/docs/metrics/briefs.jsonl", "wb").write(out)
