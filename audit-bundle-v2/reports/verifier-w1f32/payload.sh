#!/usr/bin/env bash
# payload audit: assert totalOrder=1 for every ordered payload pair (a!=b,
# same NaN class); a FAIL's got=0 reveals implementation's direction.
# Then check: for every unordered pair exactly one direction is 1.
set -u
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f32
export PATH=/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
cd "$S" || exit 9
"$PY" - <<'PYEOF'
import re
pairs = []
seen = set()
with open("p3/p3-payload-pairs.txt") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        toks = line.split()
        op, rm, a, b = toks[0], toks[1], toks[2], toks[3]
        if a == b:
            continue
        key = (op, a, b)
        if key in seen:
            continue
        seen.add(key)
        pairs.append((op, a, b))
with open("p3/p3-payload-assert.vec", "w", newline="\n") as out:
    out.write("# payload direction assertions (expect 1 where implementation orders first)\n")
    for (op, a, b) in pairs:
        out.write("%s - %s %s -> 1 -- verifier-w1f32:probe3:payload\n" % (op, a, b))
print("assertions:", len(pairs))
PYEOF
./msf_runner.exe verify p3/p3-payload-assert.vec > p3-verify-payload.log 2>&1
echo "verify exit=$?"
grep -E 'total|VERDICT' p3-verify-payload.log | head -n 4
"$PY" - <<'PYEOF'
import re
impl = {}
n_assert = 0
with open("p3/p3-payload-assert.vec") as fh:
    vecs = [l.split() for l in fh if l.strip() and not l.startswith("#")]
for i, v in enumerate(vecs, start=1):
    op, a, b = v[0], v[2], v[3]
    impl[(op, a, b)] = 1
    n_assert += 1
n_fail = 0
with open("p3-verify-payload.log") as fh:
    for line in fh:
        if line.startswith("FAIL"):
            m = re.search(r"got ([0-9a-f]+)/", line)
            vec = line.split("|", 1)[1].strip().split()
            op, a, b = vec[0], vec[2], vec[3]
            impl[(op, a, b)] = int(m.group(1))
            n_fail += 1
print("assertions=%d fails=%d" % (n_assert, n_fail))
bad = 0
checked = set()
for (op, a, b), v1 in impl.items():
    if (op, b, a) in checked or (op, a, b) in checked:
        continue
    v2 = impl.get((op, b, a))
    if v2 is None:
        continue
    checked.add((op, a, b))
    checked.add((op, b, a))
    if not ((v1 == 1 and v2 == 0) or (v1 == 0 and v2 == 1)):
        bad += 1
        print("NOT-ANTISYMMETRIC:", op, a, b, v1, v2)
print("unordered pairs checked with both directions:", len(checked) // 2, "violations:", bad)
PYEOF
