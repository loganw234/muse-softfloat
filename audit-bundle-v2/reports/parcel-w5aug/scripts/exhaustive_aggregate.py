import pathlib
import re
import sys

op = sys.argv[1]
root = pathlib.Path(__file__).resolve().parents[1] / "logs" / ("exh-" + op)
total = 0
bad = 0
kinds = {}
minnorm = 0
opp = 0
shards = sorted(root.glob("shard-*.log"))
for path in shards:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"total=(\d+) mismatches=(\d+)", text)
    assert m, path
    total += int(m.group(1))
    bad += int(m.group(2))
    assert "VERDICT: PASS" in text, path
    for name, n in re.findall(r"kind (\S+)\s+(\d+)", text):
        kinds[name] = kinds.get(name, 0) + int(n)
    mm = re.search(r"inexact-tail-to-min-normal (\d+)", text)
    minnorm += int(mm.group(1)) if mm else 0
    mm = re.search(r"inexact-tail-zero-opposite-head (\d+)", text)
    opp += int(mm.group(1)) if mm else 0
expected = 1 << 32
lines = ["exhaustive pairs %s: shards=%d total=%d expected=%d mismatches=%d"
         % (op, len(shards), total, expected, bad)]
for k in sorted(kinds):
    lines.append("  kind %-16s %d" % (k, kinds[k]))
lines.append("  inexact-tail-to-min-normal %d" % minnorm)
lines.append("  inexact-tail-zero-opposite-head %d" % opp)
lines.append("  kind sum check: %d" % sum(kinds.values()))
ok = len(shards) == 256 and total == expected and bad == 0 \
    and sum(kinds.values()) == total
lines.append("AGGREGATE: %s" % ("PASS" if ok else "FAIL"))
out = "\n".join(lines) + "\n"
(pathlib.Path(__file__).resolve().parents[1] / "logs"
 / ("exh-summary-%s.txt" % op)).write_bytes(out.encode())
print(out)
sys.exit(0 if ok else 1)
