#!/usr/bin/env bash
# build the differential harness (+ variants) - parcel use
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-trig
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p "$TMPDIR" /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out build/trig
O=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c"
CF="-std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off"
build_one() { # name extra-defines...
  local name=$1; shift
  gcc $CF -DMSF_TRIG_TEST_COUNTERS "$@" $SRC tests/trig_exhaustive.c \
    -o build/trig/$name.exe -lmpfr -lgmp > $O/build_$name.log 2>&1
  echo "$name rc=$?"; cat $O/build_$name.log
}
[ "${1:-}" = "all" ] && {
  build_one trig_stage1 -DMSF_TRIG_FORCE_START=1
  build_one trig_stage2 -DMSF_TRIG_FORCE_START=2
  build_one trig_droplimb -DMSF_TRIG_DROP_LIMB
  build_one trig_v2
}
[ "${1:-}" = "v2" ] && build_one trig_v2
[ -z "${1:-}" ] && build_one trig_exhaustive
gcc --version | head -1
