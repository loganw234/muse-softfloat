import re

def load(tree, log):
    p = f"scratch/verifier-w6augint/{tree}/b-hostrun/{log}.log"
    return open(p, encoding="utf-16").read().splitlines()

base = load("base", "base")
new = load("new", "new")

br = [l for l in base if l.startswith("RAY")]
nr = [l for l in new if l.startswith("RAY")]
assert len(br) == len(nr), (len(br), len(nr))
print("ray lines:", len(br))

OPS_KEYS = ("ops=", "s1ops=", "s2ops=", "s3ops=")
cls_mismatch = 0
nonops_mismatch = 0
ops_only = 0
s3ops_base = 0
s3ops_new = 0
examples = []

def fields(line):
    return dict(re.findall(r"(\S+?)=(\S+)", line))

for b, n in zip(br, nr):
    bf, nf = fields(b), fields(n)
    assert bf.get("id") == nf.get("id") and bf.get("kind", bf.get("fam")) is not None
    # compare non-ops fields
    bno = {k: v for k, v in bf.items() if not any(k.startswith(o.rstrip("=")) for o in ("ops", "s1ops", "s2ops", "s3ops"))}
    nno = {k: v for k, v in nf.items() if not any(k.startswith(o.rstrip("=")) for o in ("ops", "s1ops", "s2ops", "s3ops"))}
    if bno != nno:
        nonops_mismatch += 1
        if len(examples) < 10:
            keys = [k for k in set(bno) | set(nno) if bno.get(k) != nno.get(k)]
            examples.append((bf.get("id"), keys, b, n))
    else:
        # check whether any ops field moved
        bo = {k: v for k, v in bf.items() if k not in bno}
        no = {k: v for k, v in nf.items() if k not in nno}
        if bo != no:
            ops_only += 1
    if "s3ops" in bf:
        s3ops_base += int(bf["s3ops"])
        s3ops_new += int(nf["s3ops"])

print("non-ops field mismatches:", nonops_mismatch)
print("ops-only moves:", ops_only)
print("s3ops sum base/new:", s3ops_base, s3ops_new)
for e in examples:
    print("id=", e[0], "differing keys:", e[1])
    print("  base:", e[2][:300])
    print("  new :", e[3][:300])
