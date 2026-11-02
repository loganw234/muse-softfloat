#!/usr/bin/env python3
"""wv_claims.py - commit-message vs tree: operations authority changes (expect
only the 6 exact-family rows berkeley/auto -> mpfr-exact), COVERAGE status
stability (no flips parent->HEAD), pack64 byte identity already shown by blob.
"""
import pathlib
import subprocess

R = "scratch/verifier-w1prep/tmp"


def read_ops(p):
    rows = {}
    for l in pathlib.Path(p).read_text(encoding="utf-8").splitlines():
        if not l or l.startswith("#"):
            continue
        c = l.split("\t")
        if c[0] == "op":
            continue  # header row
        assert len(c) in (10, 11), (p, l[:60])
        if len(c) == 11:  # parent schema with status
            op, auth = c[0], c[8]
            assert c[7] in ("planned", "implemented"), l[:60]
        else:
            op, auth = c[0], c[7]
        rows[op] = auth
    return rows


def read_cov_status(p):
    rows = {}
    for l in pathlib.Path(p).read_text(encoding="utf-8").splitlines():
        if not l or l.startswith("#"):
            continue
        c = l.split("\t")
        if c[0] == "name":
            continue  # header row
        rows[c[0]] = (c[7], c[9])  # status, authority
    return rows


def fetch(rev, path_in_repo, out):
    p = subprocess.run(["git", "-c", "safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat",
                        "-C", "muse-softfloat", "show", rev + ":" + path_in_repo],
                       capture_output=True, text=True)
    assert p.returncode == 0, (rev, path_in_repo)
    pathlib.Path(out).write_text(p.stdout, encoding="utf-8")


fetch("36ca82e", "tables/operations.tsv", R + "/ops_parent.tsv")
fetch("de2d48c", "tables/operations.tsv", R + "/ops_head.tsv")
a = read_ops(R + "/ops_parent.tsv")
b = read_ops(R + "/ops_head.tsv")
print("operations families parent=%d head=%d" % (len(a), len(b)))
changed = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
for k in changed:
    print("AUTH-CHANGED %s: %s -> %s" % (k, a.get(k), b.get(k)))
print("authority changes: %d" % len(changed))

for rev, out in (("36ca82e", R + "/cov_parent.tsv"), ("de2d48c", R + "/cov_head.tsv")):
    fetch(rev, "docs/COVERAGE.tsv", out)
ca = read_cov_status(R + "/cov_parent.tsv")
cb = read_cov_status(R + "/cov_head.tsv")
print("coverage rows parent=%d head=%d" % (len(ca), len(cb)))
sflips = [k for k in ca if k in cb and ca[k][0] != cb[k][0]]
aflips = sorted(k for k in ca if k in cb and ca[k][1] != cb[k][1])
print("status flips: %d %s" % (len(sflips), sflips[:10]))
print("authority flips: %d" % len(aflips))
newrows = [k for k in cb if k not in ca]
delrows = [k for k in ca if k not in cb]
print("added=%d removed=%d" % (len(newrows), len(delrows)))
# every authority flip must be berkeley -> mpfr-exact on an exact-family row
bad = [k for k in aflips if not (ca[k][1] == "berkeley" and cb[k][1] == "mpfr-exact"
                                 and ("_exact_" in k or k.endswith("_exact")))]
print("nonconforming authority flips: %d %s" % (len(bad), bad[:10]))
