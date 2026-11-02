import collections, pathlib, re
log = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\directed1.log").read_text()
fails = [l for l in log.splitlines() if l.startswith("FAIL")]
by_op = collections.Counter()
by_file = collections.Counter()
samples = {}
for l in fails:
    m = re.search(r"\|\s+(msf\d+_\w+)", l)
    op = m.group(1) if m else "?"
    by_op[op] += 1
    f = l.split()[1].rsplit(":", 1)[0]
    by_file[f] += 1
    samples.setdefault(op, l)
print("by file:", dict(by_file))
print("by op:", dict(by_op))
for op, l in sorted(samples.items()):
    print(op, "=>", l[:260])
