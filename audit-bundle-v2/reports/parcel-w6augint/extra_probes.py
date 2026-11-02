"""extra_probes.py CATALOGUE DUMPOUT STREAMNEW MINI_OUT
1) Count decided rows whose dumped expansion lists contain an
   exact subnormal term (the P1=R2 exact-tiny-residual path).
2) Emit a mini catalogue with non-finite sphere inputs (inf /
   qNaN / sNaN in D, O, r) derived from catalogue row 1, to
   exercise the non-finite pair poison in both builds.
"""
import sys

rows = {}
for line in open(sys.argv[1], encoding="ascii"):
    if line.startswith("#") or not line.strip():
        continue
    f = line.rstrip("\n").split("\t")
    rows[int(f[0])] = f

s3cls = {}
for line in open(sys.argv[3], encoding="ascii"):
    if line.startswith("RAY ") and "s3=" in line:
        kv = dict(t.partition("=")[::2] for t in line.split()[1:])
        s3cls[int(kv["id"])] = kv["s3"]

def is_subnormal(b):
    return ((b >> 52) & 0x7FF) == 0 and (b & ((1 << 52) - 1)) != 0

cur = None
decided_sub = 0
decided = 0
sub_rows = []
for line in open(sys.argv[2], encoding="ascii"):
    t = line.split()
    if not t:
        continue
    if t[0] == "ROW":
        cur = int(t[1])
    elif t[0] == "EXP" and s3cls[cur] != "UNCERTAIN":
        if cur not in sub_rows and any(is_subnormal(int(x, 16)) for x in t[3:]):
            sub_rows.append(cur)
    elif t[0] == "CLS":
        if s3cls[cur] != "UNCERTAIN":
            decided += 1
print(f"decided rows: {decided}; with >=1 exact subnormal expansion term: {len(sub_rows)}")
print("first such rows:", sub_rows[:12])

base = rows[1][:]
variants = [
    (9001, 7, "7ff0000000000000", "nonfinite-probe D0=+inf"),
    (9002, 4, "7ff8000000000000", "nonfinite-probe O0=qNaN"),
    (9003, 13, "7ff0000000000001", "nonfinite-probe r=sNaN"),
    (9004, 10, "fff0000000000000", "nonfinite-probe C0=-inf"),
]
with open(sys.argv[4], "w", encoding="ascii", newline="\n") as out:
    out.write("# mini non-finite probe catalogue (scratch)\n")
    for rid, field, bits, prov in variants:
        f = base[:]
        f[0] = str(rid)
        f[1] = "nonfinite"
        f[3] = prov
        f[field] = bits
        out.write("\t".join(f) + "\n")
print("mini catalogue written:", sys.argv[4])
