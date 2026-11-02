"""Restate the parcel-w6popups briefs.jsonl row with a byte-level substring
swap: every other byte of the file is untouched (CRLF preserved)."""
from pathlib import Path

P = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-popups\docs\metrics\briefs.jsonl")
raw = P.read_bytes()
old = b"(20 parcels, 3 escalations,"
new = b"(19 parcels, 20 escalation filings with 3 fixes,"
assert raw.count(old) == 1, "expected exactly one match, found %d" % raw.count(old)
P.write_bytes(raw.replace(old, new))
print("restated; rows:", raw.count(b"\n"))
after = P.read_bytes()
assert after.count(b"\n") == 39
assert after.count(new) == 1
print("BYTE_SWAP_OK")
