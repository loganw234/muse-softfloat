#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-minmax || exit 9
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4minmax
C=$S/controls
mkdir -p "$C"
R=build/smoke/msf_runner.exe
MM=exact-py-t2:directed-minmax
PL=exact-py-t2:directed-payload

# positive counterparts (must PASS): the correct form of every line below
printf '%s\n' \
"msf32_minimum_number - 7f800001 3f800000 -> 3f800000 01 $MM" \
"msf32_minimum - 7fc00001 3f800000 -> 7fc00001 00 $MM" \
"msf32_minimum - 0 80000000 -> 80000000 00 $MM" \
"msf32_maximum - 0 80000000 -> 0 00 $MM" \
"msf32_minimum_magnitude - 3f800000 bf800000 -> bf800000 00 $MM" \
"msf32_set_payload_signaling - 3f800000 -> 7f800001 -- $PL" \
"msf32_set_payload - 0 -> 7fc00000 -- $PL" \
"msf32_set_payload - bf800000 -> 0 -- $PL" \
"msf32_set_payload - 7f800001 -> 0 -- $PL" \
"msf32_get_payload - 7fc00001 -> 3f800000 -- $PL" \
> "$C/positive.vec"

# 1 ignored-sNaN invalid stripped
printf '%s\n' "msf32_minimum_number - 7f800001 3f800000 -> 3f800000 00 $MM" > "$C/c1-ignored-snan-invalid-stripped.vec"
# 2 plain/Number swapped on single-qNaN
printf '%s\n' "msf32_minimum - 7fc00001 3f800000 -> 3f800000 00 $MM" > "$C/c2-plain-number-swapped.vec"
# 3 -0/+0 selections swapped
printf '%s\n' "msf32_minimum - 0 80000000 -> 0 00 $MM" "msf32_maximum - 0 80000000 -> 80000000 00 $MM" > "$C/c3-zero-sign-swapped.vec"
# 4 magnitude tie-break corrupted
printf '%s\n' "msf32_minimum_magnitude - 3f800000 bf800000 -> 3f800000 00 $MM" > "$C/c4-magnitude-tiebreak.vec"
# 5 NaN payload altered
printf '%s\n' "msf32_minimum - 7fc00001 3f800000 -> 7fc00002 00 $MM" > "$C/c5-nan-payload-altered.vec"
# 6 quiet bit flipped on signaling setter
printf '%s\n' "msf32_set_payload_signaling - 3f800000 -> 7fc00001 -- $PL" > "$C/c6-quiet-bit-flipped.vec"
# 7 setPayload(0) expected +0
printf '%s\n' "msf32_set_payload - 0 -> 0 -- $PL" > "$C/c7-setpayload0-pluszero.vec"
# 8 inadmissible input expected NaN
printf '%s\n' "msf32_set_payload - bf800000 -> 7fc00000 -- $PL" "msf32_set_payload - 7f800001 -> 7fc00001 -- $PL" > "$C/c8-inadmissible-nan.vec"
# 9 flags token 00 where -- required
printf '%s\n' "msf32_get_payload - 7fc00001 -> 3f800000 00 $PL" > "$C/c9-flags-token.vec"

fail=0
"$R" verify "$C/positive.vec" > "$C/positive.log" 2>&1
rc=$?
echo "positive counterparts: rc=$rc (want 0)"
grep -E '^(total|VERDICT)' "$C/positive.log" || true
[ $rc -eq 0 ] || fail=1
for f in "$C"/c*.vec; do
  name=$(basename "$f" .vec)
  "$R" verify "$f" > "$C/$name.log" 2>&1
  rc=$?
  sig=$(grep -E '^(FAIL|total|VERDICT)' "$C/$name.log" | head -3 | tr '\n' ' ')
  if [ $rc -ne 0 ]; then echo "control $name: REFUSED rc=$rc | $sig"; else echo "control $name: NOT REFUSED rc=0 | $sig"; fail=1; fi
done
[ $fail -eq 0 ] && echo CONTROLS-ALL-REFUSED || echo CONTROLS-FAILED
exit $fail
