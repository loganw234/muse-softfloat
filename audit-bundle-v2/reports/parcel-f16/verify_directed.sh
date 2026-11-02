#!/usr/bin/env bash
# usage: verify_directed.sh <vecfile...> (verify each separately, log)
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w2-f16 || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f16/tmp
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f16/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
R=build/smoke/msf_runner.exe
fail=0
for f in "$@"; do
  tag=$(basename "$f" .vec)
  log=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f16/verify-$tag.log
  t0=$(date +%s)
  "$R" verify "$f" > "$log" 2>&1
  rc=$?
  t1=$(date +%s)
  echo "$tag rc=$rc wall=$((t1-t0))s $(grep '^total' "$log") $(grep '^VERDICT' "$log")"
  if [ $rc -ne 0 ]; then
    fail=1
    grep '^FAIL' "$log" | head -20
  fi
done
exit $fail
