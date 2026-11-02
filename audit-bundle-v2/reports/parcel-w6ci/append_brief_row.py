import hashlib
import json
import pathlib

root = pathlib.Path(__file__).resolve().parents[2]
path = root / "worktrees/w6-ci/docs/metrics/briefs.jsonl"
before = path.read_bytes()
print("before bytes", len(before), "sha256", hashlib.sha256(before).hexdigest())
assert before.endswith(b"\n") and not before.endswith(b"\r\n")

row = {
    "wave": "wave6",
    "work": "Library CI on Linux: GitHub Actions smoke+standard jobs on Ubuntu (.github/workflows/ci.yml) plus two portability-only guards in tools/run.sh (MSYS2 PATH prepend, python3 fallback); standard verdicts byte-identical on the Windows host before/after",
    "author": "parcel-w6ci",
    "base": "50aac59f6035d56c37340ff07c59252cfd22d5d4",
    "time_box_min": 360,
    "ceiling_lines": 0,
    "ceiling_text": "no line ceiling stated in brief w6-ci.md; owned-files list is the bound (.github/workflows/ci.yml, tools/run.sh portability only, this row)",
}
line = (json.dumps(row, ensure_ascii=True) + "\n").encode("ascii")
with open(path, "ab") as f:
    f.write(line)

after = path.read_bytes()
print("after bytes", len(after), "sha256", hashlib.sha256(after).hexdigest())
print("prefix unchanged:", after[: len(before)] == before)
print("appended bytes:", len(after) - len(before))
json.loads(line)
print("row parses as JSON: OK")
print("total rows:", after.count(b"\n"))
