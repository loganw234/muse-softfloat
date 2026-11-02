"""append_brief_row.py - binary-append this parcel's row to
docs/metrics/briefs.jsonl (append-only, byte-exact existing rows).
Asserts the file currently ends with LF and that no w6augint row
exists yet; writes exactly one LF-terminated row.
"""
import json
import sys

PATH = "worktrees/w6-augint/docs/metrics/briefs.jsonl"
data = open(PATH, "rb").read()
assert data.endswith(b"\n"), "file does not end with LF"
assert b"parcel-w6augint" not in data, "row already present"

row = {
    "wave": "wave6",
    "work": "Wave 6 queue item 1: interval workload stage 3 consumes Clause 9.5 augmented pairs (aug_sum/aug_prod replace TwoSum/FMA-TwoProduct, guard re-derived: quiet iff every pair exact and finite); catalogue classifications identical to base on all 710 rows, stage-3 counted calls 283314 -> 63305",
    "author": "parcel-w6augint",
    "base": "50aac59f6035d56c37340ff07c59252cfd22d5d4",
    "time_box_min": 720,
    "ceiling_lines": 0,
    "ceiling_text": "no line ceiling stated in brief w6-augint.md; owned-files list is the bound (board/interval_workload.c, board/interval_workload.h, this row)",
}
line = (json.dumps(row, ensure_ascii=True) + "\n").encode("ascii")
with open(PATH, "ab") as f:
    f.write(line)
after = open(PATH, "rb").read()
assert after[: len(data)] == data and len(after) == len(data) + len(line)
print(f"appended {len(line)} bytes; file now {len(after)} bytes; rows preserved byte-exact")
