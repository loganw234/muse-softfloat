"""Append this parcel's briefs.jsonl row, binary append only.

Reads the file first to record its length and hash, asserts it
ends with LF, then appends exactly one LF-terminated JSON
line in a single write. Verifies the old bytes are a strict
prefix of the result (append-only, byte-exact elsewhere).
"""
import hashlib
import json

PATH = ("C:/Users/logan/source/repos/Muse-Softfloat/worktrees/"
        "w6-examples/docs/metrics/briefs.jsonl")

before = open(PATH, "rb").read()
assert before.endswith(b"\n"), "file does not end with LF"
before_lines = before.count(b"\n")
print(f"before: {len(before)} bytes, {before_lines} lines, "
      f"sha256={hashlib.sha256(before).hexdigest()}")

row = {
    "wave": "wave6",
    "work": ("Wave 6 queue item 4: examples on-ramp (host "
             "public-API program with pinned expected output "
             "and one-command build/run/diff, Pico twin "
             "printing the same lines over USB CDC, "
             "examples README, additive example-host CI job)"),
    "author": "parcel-w6examples",
    "base": "537b08edce17112da8f84353abcb2c693f2a5e65",
    "time_box_min": 360,
    "ceiling_lines": 0,
    "ceiling_text": ("no line ceiling stated in brief "
                     "w6-examples.md; owned-files list is the "
                     "bound (examples/**, .github/workflows/"
                     "ci.yml new job only, this row)"),
}
line = (json.dumps(row) + "\n").encode("utf-8")
assert b"\r" not in line

with open(PATH, "ab") as f:
    f.write(line)

after = open(PATH, "rb").read()
assert after.startswith(before), "existing bytes changed"
assert len(after) == len(before) + len(line), "length delta wrong"
assert after.count(b"\n") == before_lines + 1, "line count wrong"
parsed = json.loads(after[len(before):].decode("utf-8"))
assert parsed == row, "appended line does not round-trip"
print(f"after:  {len(after)} bytes, {after.count(bytes([10]))} lines, "
      f"sha256={hashlib.sha256(after).hexdigest()}")
print(f"appended {len(line)} bytes; old content is strict prefix: True")
