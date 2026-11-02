#!/usr/bin/env bash
set -euo pipefail
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/parcel-xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-xf\tmp'
export TEMP="$TMP"
mkdir -p "$TMPDIR"
bash "$ROOT/softfloat-bootstrap-kit/tools/ledger.sh" append "$ROOT/ledger" parcel-xf \
  "Design: 126 xf rows as wrappers on landed format-generic kernels; one objection on f64 trap wording" \
  < "$ROOT/scratch/parcel-xf/design-body.md"
printf 'For: lead\nObjection before coding around it: brief asks convert-then-operate traps at least one per arithmetic family per dest. For dest f64 convert-first is exact (f16/f32 widen, f64 identity), so no such trap exists for add/sub/mul/div/sqrt to f64. Design entry in ledger/parcel-xf.md names my substitution (unfused-fma and via-binary32 intermediate traps per f64 family, plus sampled zero-difference proof for convert-first). Source code unaffected; proceeding with src and f32 traps, will reshape only tests if you rule otherwise.\n' \
  | bash "$ROOT/softfloat-bootstrap-kit/tools/ledger.sh" urgent "$ROOT/ledger" parcel-xf f64-trap-objection \
      "parcel-xf objection: dest-f64 convert-first traps are vacuous; substitution named in design entry"
echo OK
