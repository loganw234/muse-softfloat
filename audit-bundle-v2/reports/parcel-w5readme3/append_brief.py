"""append_brief.py - append this parcel's briefs.jsonl row (last).

Append-only: proves the old bytes survive as a prefix, the new row
parses with the established field set, and the row is last.
"""
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parents[2] / "worktrees" / "w5-readme3" / "docs" / "metrics" / "briefs.jsonl"
old = P.read_bytes()
old_rows = [json.loads(x) for x in old.decode("utf-8").splitlines() if x.strip()]
print(f"before: {len(old_rows)} rows, sha256 {hashlib.sha256(old).hexdigest()}")
print("last before:", old_rows[-1]["author"], old_rows[-1]["work"][:60])
assert not any(r.get("author") == "parcel-w5readme3" for r in old_rows), "row already present"

row = {
    "wave": "wave5",
    "work": "Wave 5 close README + site refresh at SF-2 close (849 instantiations, Tier 2 66/66; WASM rebuilt, 1,620-vector replay 0 mismatches; 9 augmented pairs excluded by shape with printed exclusion)",
    "author": "parcel-w5readme3",
    "base": "e9c57fb8c100913502d67242cad0d0729b7ce46a",
    "time_box_min": 360,
    "ceiling_lines": 0,
    "ceiling_text": "no line ceiling stated in brief w5-readme3.md; owned-files list is the bound (README.md, site/**, this row), generated data/wasm excluded",
}
line = (json.dumps(row, ensure_ascii=True) + "\n").encode("utf-8")
assert old.endswith(b"\n"), "file does not end with newline - refuse to guess"
P.write_bytes(old + line)
new = P.read_bytes()
assert new[:len(old)] == old, "prefix changed!"
rows = [json.loads(x) for x in new.decode("utf-8").splitlines() if x.strip()]
print(f"after: {len(rows)} rows, sha256 {hashlib.sha256(new).hexdigest()}")
assert rows[-1] == row, "new row is not last"
keys = {tuple(sorted(r.keys())) for r in rows[-4:]}
print("key sets of last 4 rows:", keys)
print("APPEND OK")
