"""17_seam.py - seam census: counts, claims, hypot planned-only,
math_bin dispatch trace data, inventory incl. mutants, regen compare."""
import subprocess
import sys

COPY = "worktrees/verify5-alg1"


def read_tsv(path):
    with open(path, encoding="utf-8") as fh:
        rows = [l.rstrip("\n").split("\t") for l in fh
                if l.strip() and not l.startswith("#")]
    return rows[0], rows[1:]


def inventory(coverage_path):
    hdr, rows = read_tsv(coverage_path)
    col = {name: i for i, name in enumerate(hdr)}
    t1 = t1i = t2 = t2i = t2p = bad = 0
    planned_names = []
    for r in rows:
        tier, status, claim = r[col["tier"]], r[col["status"]], r[col["claim"]]
        if status not in ("implemented", "planned"):
            bad += 1
        if tier == "1":
            t1 += 1
            if status == "implemented":
                t1i += 1
            if claim != "required":
                bad += 1
        elif tier == "2":
            t2 += 1
            if status == "implemented":
                t2i += 1
            elif status == "planned":
                t2p += 1
                planned_names.append(r[col["name"]])
            if claim != "C-754":
                bad += 1
        else:
            bad += 1
    return t1, t1i, t2, t2i, t2p, bad, planned_names


def main():
    # 1. operations.tsv Tier 2 rows
    hdr, rows = read_tsv("%s/tables/operations.tsv" % COPY)
    col = {n: i for i, n in enumerate(hdr)}
    t2ops = [r for r in rows if r[col["tier"]] == "2"]
    print("operations.tsv: %d Tier-2 rows (of %d total)" % (len(t2ops), len(rows)))
    for r in t2ops:
        if r[col["op"]] in ("r_sqrt", "hypot"):
            print("  op=%s std=%s sig=%s claim=%s" % (
                r[col["op"]], r[col["std_name"]], r[col["sig"]], r[col["claim"]]))
    # 2. implemented.tsv r_sqrt/hypot presence
    _, impl = read_tsv("%s/tables/implemented.tsv" % COPY)
    names = [r[0] for r in impl]
    print("implemented.tsv rows: %d" % len(names))
    print("  r_sqrt rows: %d" % sum(1 for n in names if n.endswith("_r_sqrt")))
    print("  hypot rows: %d (planned-only requires 0)" % sum(
        1 for n in names if n.endswith("_hypot")))
    # 3. COVERAGE inventory
    t1, t1i, t2, t2i, t2p, bad, planned = inventory(
        "%s/docs/COVERAGE.tsv" % COPY)
    print("COVERAGE inventory: tier1 %d implemented of %d; "
          "tier2 %d implemented, %d planned, %d registered; bad=%d"
          % (t1i, t1, t2i, t2p, t2, bad))
    print("tier2 planned names: %s" % " ".join(sorted(set(planned))))
    # claim tokens
    hdr2, cov = read_tsv("%s/docs/COVERAGE.tsv" % COPY)
    cc = {n: i for i, n in enumerate(hdr2)}
    claims = sorted(set(r[cc["claim"]] for r in cov))
    print("claim tokens in COVERAGE: %s" % claims)
    ok = (t1 == 783 and t1i == 783 and t2 == 45 and t2i == 42
          and t2p == 3 and bad == 0 and claims == ["C-754", "required"])
    print("inventory gate: %s" % ("PASS" if ok else "FAIL"))
    # 4. mutants (mirror of run.sh controls 9)
    import shutil
    cov_path = "%s/docs/COVERAGE.tsv" % COPY
    with open(cov_path, encoding="utf-8") as fh:
        lines = fh.readlines()
    hdr_line = [l for l in lines if l.startswith("name")][0]
    # flip first tier-1 implemented -> planned
    done = False
    m1 = []
    for l in lines:
        if l.startswith("#") or l.startswith("name") or done:
            m1.append(l)
            continue
        f = l.rstrip("\n").split("\t")
        if f[cc["tier"]] == "1" and f[cc["status"]] == "implemented":
            f[cc["status"]] = "planned"
            done = True
        m1.append("\t".join(f) + "\n")
    open("scratch/verifier-w5alg1/out/cov-flip.tsv", "w").writelines(m1)
    r1 = inventory("scratch/verifier-w5alg1/out/cov-flip.tsv")
    print("mutant tier1-planned-flip refused: %s" % ("yes" if not (
        r1[0] == 783 and r1[1] == 783 and r1[2] == 45 and r1[5] == 0) else "NO"))
    # delete first tier-2 row
    done = False
    m2 = []
    for l in lines:
        if l.startswith("#") or l.startswith("name"):
            m2.append(l)
            continue
        f = l.rstrip("\n").split("\t")
        if not done and f[cc["tier"]] == "2":
            done = True
            continue
        m2.append(l)
    open("scratch/verifier-w5alg1/out/cov-del.tsv", "w").writelines(m2)
    r2 = inventory("scratch/verifier-w5alg1/out/cov-del.tsv")
    print("mutant tier2-row-deleted refused: %s" % ("yes" if not (
        r2[2] == 45 and r2[5] == 0) else "NO"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
