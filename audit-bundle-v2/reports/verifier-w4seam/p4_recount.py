#!/usr/bin/env python3
# p4_recount.py - independent table recount. Fresh parse of the TSVs only;
# no generator imports. Reads the COPY's tables + generated files.
import pathlib

COPY = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\verify4-seam")
SCR = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w4seam")

def read_tsv(path):
    rows, header = [], None
    for line in path.read_text(encoding="utf-8").split("\n"):
        if not line or line.startswith("#"):
            continue
        cells = line.split("\t")
        if header is None:
            header = cells
        else:
            assert len(cells) == len(header), (path, line)
            rows.append(dict(zip(header, cells)))
    return header, rows

_, ops = read_tsv(COPY / "tables" / "operations.tsv")
_, cov = read_tsv(COPY / "docs" / "COVERAGE.tsv")
_, impl = read_tsv(COPY / "tables" / "implemented.tsv")

out = []
t1fam = [r for r in ops if r["tier"] == "1"]
t2fam = [r for r in ops if r["tier"] == "2"]
out.append("families: tier1=%d tier2=%d total=%d" % (len(t1fam), len(t2fam), len(ops)))
out.append("tier1 claims: %s" % sorted({r["claim"] for r in t1fam}))
out.append("tier2 claims: %s" % sorted({r["claim"] for r in t2fam}))
out.append("tier2 authorities: %s" % sorted({r["authority"] for r in t2fam}))
out.append("tier2 comparisons: %s" % sorted({r["comparison"] for r in t2fam}))
out.append("tier2 sig/rounding/flags: %s" % sorted({(r["sig"], r["rounding"], r["flags"]) for r in t2fam}))
out.append("tier2 waves: %s" % sorted({r["wave"] for r in t2fam}))

# expansion shape: homogeneous pair (f16,f32,f64 dest=src) -> 3 per family;
# homogeneous unary -> 3 per family. Every Tier 2 family must yield 3.
t2names = sorted({r["op"] for r in t2fam})
out.append("tier2 family names (%d): %s" % (len(t2names), ",".join(t2names)))

t1cov = [r for r in cov if r["tier"] == "1"]
t2cov = [r for r in cov if r["tier"] == "2"]
out.append("coverage rows: tier1=%d (impl=%d) tier2=%d (impl=%d planned=%d)" % (
    len(t1cov), sum(1 for r in t1cov if r["status"] == "implemented"),
    len(t2cov), sum(1 for r in t2cov if r["status"] == "implemented"),
    sum(1 for r in t2cov if r["status"] == "planned")))
out.append("implemented.tsv rows: %d" % len(impl))

# every Tier 2 name at exactly three formats (dest f16/f32/f64)
for n in t2names:
    rows = [r for r in t2cov if r["name"].endswith("_" + n)]
    out.append("t2 family %-28s rows=%d dests=%s" % (n, len(rows), sorted({r["dest"] for r in rows})))

# dispatch: tier2 planned entries carry NULL calls
disp = (COPY / "tests" / "msf_dispatch.h").read_text(encoding="utf-8")
import re
entries = re.findall(r'\{ "(\w+)", "([\w]+)", MSF_SIG_\w+, [\w]+, \{ [\w, ]+ \}, (\d+), (\d+), (\d+), (\d+), (\d+), (\w+) \}', disp)
t2entry = [e for e in entries if e[0] in {r["name"] for r in t2cov}]
out.append("dispatch tier2 entries: %d (null-call=%d status0=%d)" % (
    len(t2entry), sum(1 for e in t2entry if e[7] == "0"), sum(1 for e in t2entry if e[5] == "0")))
nonnull = [e[0] for e in t2entry if e[7] != "0"]
out.append("tier2 entries with non-null call: %s" % (nonnull if nonnull else "none"))
badflag = [(e[0], e[4]) for e in t2entry]
covflag = {r["name"]: r["flags"] for r in t2cov}
mismatch = [(n, "dispatch_has_flags=%s coverage_flags=%s" % (h, covflag.get(n))) for n, h in badflag if (h == "1") != (covflag.get(n) == "yes")]
out.append("dispatch has_flags vs coverage flags mismatches: %s" % (mismatch if mismatch else "none"))

# header: tier2 decls present and comments say planned
hdr = (COPY / "include" / "muse_softfloat.h").read_text(encoding="utf-8")
t2names_cov = {r["name"] for r in t2cov}
missing = [n for n in t2names_cov if n + "(" not in hdr]
out.append("tier2 names missing from header: %s" % (missing if missing else "none"))
unplanned = [n for n in t2names_cov if not re.search(r"/\* %s [\s\S]{0,80}?planned \*/\n\w+ %s\(" % (re.escape({r["name"]: r["std_name"] for r in t2cov}[n]), re.escape(n)), hdr)]
out.append("tier2 decls not marked planned: %s" % (unplanned if unplanned else "none"))

(SCR / "recount.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
