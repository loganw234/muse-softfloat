"""Sum the 32 f32 shard logs; require the exact finite total."""
import glob
import re
import sys

EXPECT_CHECKED = 4278190080 * 8  # finite encodings x 2 fn x 4 modes
tot = {"checked": 0, "mismatches": 0, "undecided": 0,
       "decider_escalations": 0, "specials": 0, "audits": 0,
       "audit_fail": 0}
stage = [0, 0, 0]
final_un = 0
logs = sorted(glob.glob("scratch/parcel-w4trig/out/f32shards/shard_*.log"))
print(f"shard logs: {len(logs)}")
ok = len(logs) == 32
for path in logs:
    txt = open(path).read()
    m = re.search(
        r"checked=(\d+) mismatches=(\d+) undecided=(\d+) "
        r"decider_escalations=(\d+) specials=(\d+) audits=(\d+) "
        r"audit_fail=(\d+) -> (\w+)", txt)
    if not m:
        print("NO SUMMARY", path)
        ok = False
        continue
    vals = [int(m.group(i)) for i in range(1, 8)]
    for k, v in zip(tot, vals):
        tot[k] += v
    if m.group(8) != "PASS":
        print("SHARD NOT PASS", path)
        ok = False
    c = re.search(r"stage hits (\d+)/(\d+)/(\d+) final_undecided=(\d+)", txt)
    if c:
        for i in range(3):
            stage[i] += int(c.group(i + 1))
        final_un += int(c.group(4))
print("totals:", tot)
print(f"stage hits sum {stage} final_undecided sum {final_un}")
print(f"expected checked {EXPECT_CHECKED}")
verdict = (ok and tot["checked"] == EXPECT_CHECKED
           and tot["mismatches"] == 0 and tot["undecided"] == 0
           and tot["audit_fail"] == 0 and final_un == 0)
print("F32 EXHAUSTIVE:", "PASS" if verdict else "FAIL")
sys.exit(0 if verdict else 1)
