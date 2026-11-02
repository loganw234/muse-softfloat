"""Exact re-sum of f32 shard logs (independent of driver awk)."""
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
logs = sorted(root.glob("shard-*.log"))
assert len(logs) == 256, len(logs)
tot = dict(checked=0, mismatches=0, undecided=0, escalations=0,
           specials=0, shortcuts=0, audits=0, audit_fail=0)
stage = [0, 0, 0]
final_bad = []
nonpass = []
ranges = []
for p in logs:
    text = p.read_text(errors="replace")
    m = re.search(r"f32 range: checked=(\d+) mismatches=(\d+) "
                  r"undecided=(\d+) escalations=(\d+) specials=(\d+) "
                  r"shortcuts=(\d+) audits=(\d+) audit_fail=(\d+) -> (\w+)",
                  text)
    assert m, p.name
    vals = [int(x) for x in m.groups()[:8]]
    for k, v in zip(tot, vals):
        tot[k] += v
    if m.group(9) != "PASS":
        nonpass.append(p.name)
    c = re.search(r"counters: stage hits (\d+)/(\d+)/(\d+) "
                  r"final_undecided=(\d+)", text)
    assert c, p.name
    for i in range(3):
        stage[i] += int(c.group(i + 1))
    if int(c.group(4)) != 0:
        final_bad.append(p.name)
    r = re.search(r"f32 range \[([0-9a-f]+),([0-9a-f]+)\) fn=(\d+) "
                  r"inputs_per_fn=(\d+)", text)
    assert r, p.name
    ranges.append((int(r.group(1), 16), int(r.group(2), 16),
                   int(r.group(3)), int(r.group(4))))
    assert "MISMATCH" not in text and "UNDECIDED" not in text, p.name
    assert "X-AUDIT-FAIL" not in text, p.name
# range coverage: contiguous [0, 2^32), fn=4, 2^24 each
ranges.sort()
assert ranges[0][0] == 0 and ranges[-1][1] == 1 << 32
for i in range(1, 256):
    assert ranges[i][0] == ranges[i - 1][1], i
assert all(r[2] == 4 and r[3] == 1 << 24 for r in ranges)
print(f"shards=256 ranges contiguous [0,2^32) fn=4 ok")
print(tot)
print(f"stage hits: {stage[0]}/{stage[1]}/{stage[2]}")
print(f"final_undecided shards: {final_bad}")
print(f"nonpass shards: {nonpass}")
expect = (1 << 32) * 2 * 5
print(f"expected checked (2^32 x 2fn x 5modes) = {expect} "
      f"match={tot['checked'] == expect}")
