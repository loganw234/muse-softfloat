import json, subprocess

repo = "muse-softfloat"
ours = subprocess.check_output(["git", "-C", repo, "show", ":2:docs/metrics/briefs.jsonl"])
theirs = subprocess.check_output(["git", "-C", repo, "show", ":3:docs/metrics/briefs.jsonl"])
base = subprocess.check_output(["git", "-C", repo, "show",
                                 "cdc40ae:docs/metrics/briefs.jsonl"])
base_rows = [x for x in base.decode("utf-8").splitlines() if x.strip()]
our_rows = [x for x in ours.decode("utf-8").splitlines() if x.strip()]
their_rows = [x for x in theirs.decode("utf-8").splitlines() if x.strip()]
assert our_rows[:len(base_rows)] == base_rows
assert their_rows[:len(base_rows)] == base_rows
new_theirs = their_rows[len(base_rows):]
our_authors = [json.loads(x)["author"] for x in our_rows]
for x in new_theirs:
    assert json.loads(x)["author"] not in our_authors, x[:80]
out = ours
if not out.endswith(b"\n"):
    out += b"\n"
for x in new_theirs:
    out += (x + "\n").encode("utf-8")
rows = [json.loads(x) for x in out.decode("utf-8").splitlines() if x.strip()]
print("rows:", len(rows), "tail authors:",
      [r["author"] for r in rows[-(len(new_theirs) + 1):]])
open(repo + "/docs/metrics/briefs.jsonl", "wb").write(out)
