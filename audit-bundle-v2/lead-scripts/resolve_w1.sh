#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
export TMPDIR=$PWD/../scratch/lead/tmp
git show :2:tables/implemented.tsv > ../scratch/lead/impl-ours.tsv
git show :3:tables/implemented.tsv > ../scratch/lead/impl-theirs.tsv
../.venv/Scripts/python.exe - <<'EOF'
ours = open("../scratch/lead/impl-ours.tsv", "rb").read().decode().replace("\r\n", "\n").splitlines()
theirs = open("../scratch/lead/impl-theirs.tsv", "rb").read().decode().replace("\r\n", "\n").splitlines()
seen = {l.split("\t")[0] for l in ours if l and not l.startswith("#")}
extra = [l for l in theirs if l and not l.startswith("#") and l.split("\t")[0] not in seen]
rows = [l for l in ours if l.strip()] + extra
names = [l.split("\t")[0] for l in rows if not l.startswith("#")]
assert len(names) == len(set(names)), "dup names"
impl = [l for l in names if l != "name"]
print("union rows:", len(rows), "implemented:", len(impl))
assert len(impl) == 409, len(impl)
open("tables/implemented.tsv", "wb").write(("\n".join(rows) + "\n").encode())
EOF
echo union_rc=$?
../.venv/Scripts/python.exe tools/gen_tables.py
git add tables/implemented.tsv docs/COVERAGE.tsv include/muse_softfloat.h tests/msf_dispatch.h src/msf_formats.h
git status --short | head
