"""compare_streams.py BASE NEW CATALOGUE
Full-stream comparison of two interval_host outputs: every RAY
field must match except ops counters; ops counters outside
stage 3 must also match. Then containment of NEW against the
catalogue's exact column (sphere rows): any decided stage/final
class must equal the exact class.
"""
import sys

OPS_FIELDS = {"s3ops"}
ALL_OPS = {"s1ops", "s2ops", "s3ops", "ops", "evals"}


def parse(path):
    rows = {}
    summary = None
    for line in open(path, encoding="ascii"):
        line = line.strip()
        if line.startswith("RAY "):
            kv = {}
            for tok in line.split()[1:]:
                k, _, v = tok.partition("=")
                kv[k] = v
            rows[int(kv["id"])] = kv
        elif line.startswith("SUMMARY"):
            summary = line
    return rows, summary


def main():
    base, bsum = parse(sys.argv[1])
    new, nsum = parse(sys.argv[2])
    exact = {}
    for line in open(sys.argv[3], encoding="ascii"):
        if line.startswith("#") or not line.strip():
            continue
        f = line.rstrip("\n").split("\t")
        exact[int(f[0])] = (f[2], f[16])

    assert set(base) == set(new), "row id sets differ"
    bad = []
    s3_base = s3_new = 0
    for rid in sorted(base):
        b, n = base[rid], new[rid]
        assert set(b) == set(n), f"id {rid} field sets differ"
        for k in b:
            if k in OPS_FIELDS:
                continue
            if b[k] != n[k]:
                bad.append((rid, k, b[k], n[k]))
        if "s3ops" in b:
            s3_base += int(b["s3ops"])
            s3_new += int(n["s3ops"])
    print(f"rows compared: {len(base)}")
    print(f"non-ops field mismatches: {len(bad)}")
    for row in bad[:20]:
        print("  MISMATCH", row)
    print(f"sphere s3ops total: base={s3_base} new={s3_new} delta={s3_new - s3_base}")

    wrong = []
    for rid, kv in new.items():
        kind, ex = exact[rid]
        if kind != "sphere":
            continue
        for stage in ("s1", "s2", "s3", "final"):
            got = kv[stage]
            if got != "UNCERTAIN" and got != ex:
                wrong.append((rid, stage, got, ex))
    print(f"containment (new vs catalogue exact, sphere): decided-wrong={len(wrong)}")
    for row in wrong[:20]:
        print("  WRONG", row)
    print("base:", bsum)
    print("new :", nsum)
    return 1 if bad or wrong else 0


if __name__ == "__main__":
    sys.exit(main())
