#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/worktrees/verify3-str" || exit 9
echo "=== VECS line:"
grep -n '^VECS=' tools/run.sh | tr ' ' '\n' | grep -c vec
grep -n 'str\.vec' tools/run.sh || echo "no str.vec in run.sh"
echo "=== control 9 lines:"
sed -n '170,175p' tools/run.sh
echo "=== probe runner: control-9 planned vector outcome:"
printf 'msf16_from_decimal te 1.0 -> 3c00 00 control:planned\n' > "$R/scratch/verifier-w3str/planned.vec"
"$R/scratch/verifier-w3str/runner.exe" verify "$R/scratch/verifier-w3str/planned.vec" 2>&1 | tail -5
echo "=== implemented.tsv line-ending mix:"
grep -c $'\r' tables/implemented.tsv
wc -l tables/implemented.tsv
