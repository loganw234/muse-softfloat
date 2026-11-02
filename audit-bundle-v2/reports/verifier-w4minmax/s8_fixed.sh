#!/usr/bin/env bash
# verifier-w4minmax s8: scratch fixed-runner experiment (copy sources to
# scratch, apply 3 one-line pin restorations, build, replay) + header
# recheck + MPFR finite-value corroboration.
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-minmax
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4minmax
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
OUT=$SCR/out-fixed
rm -rf "$OUT"
mkdir -p "$OUT/fxsrc" "$OUT/fxinc"
cd "$COPY" || exit 9
cp src/*.c src/*.h src/*.inc "$OUT/fxsrc/" 2>/dev/null
cp src/*.h src/*.inc "$OUT/fxsrc/" 2>/dev/null
cp include/muse_softfloat.h "$OUT/fxinc/"
cp tests/runner.c tests/sha256.c tests/sha256.h "$OUT/"
F="$OUT/fxsrc/msf_performat.inc"
grep -n 'a->sign ? 1 : -1' "$F"
grep -n 'MSF_VC_QUIET_NAN' "$F" | head -3
grep -n 'signaling ? MSF_PF_C(QUIET_BIT)' "$F"
sed -i 's/return a->sign ? 1 : -1; \/\* -0 below +0 (9.6) \*\//return a->sign ? -1 : 1; \/* -0 below +0 (9.6) *\//' "$F"
sed -i 's/if ((an ? da.cls : db.cls) == MSF_VC_QUIET_NAN)/if ((an ? da.cls : db.cls) == MSF_VC_SIGNALING_NAN)/' "$F"
sed -i 's/(signaling ? MSF_PF_C(QUIET_BIT) : 0u)/(signaling ? 0u : MSF_PF_C(QUIET_BIT))/' "$F"
echo "== fixed lines =="
grep -n 'a->sign ? -1 : 1' "$F"
grep -n 'MSF_VC_SIGNALING_NAN)' "$F" | head -3
grep -n 'signaling ? 0u' "$F"
diff "$COPY/src/msf_performat.inc" "$F" | head -20
echo "== diff line count: $(diff "$COPY/src/msf_performat.inc" "$F" | grep -c '^[<>]') =="
/c/msys64/mingw64/bin/gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -DMSF_BUILD_ID='"fixed-experiment"' -I "$OUT/fxinc" -I "$OUT/fxsrc" "$OUT/fxsrc"/msf16.c "$OUT/fxsrc"/msf32.c "$OUT/fxsrc"/msf64.c "$OUT/fxsrc"/msf_flags.c "$OUT/fxsrc"/msf_wide.c "$OUT/fxsrc"/msf_roundpack.c "$OUT/fxsrc"/msf_string.c "$OUT/runner.c" "$OUT/sha256.c" -o "$OUT/fx_runner.exe" 2>"$OUT/fx-build.log"
echo "fx_build_rc=$?"
tail -3 "$OUT/fx-build.log"
FX="$OUT/fx_runner.exe"
echo "== fixed runner: committed minmax (generator-true) =="
"$FX" verify tests/vectors/minmax-f16.vec tests/vectors/minmax-f32.vec tests/vectors/minmax-f64.vec > "$OUT/fx-minmax.log" 2>&1
echo "fx_minmax_rc=$? $(grep -E '^total' "$OUT/fx-minmax.log")"
echo "== fixed runner: committed payload UNFIXED (expect exactly 1 fail: f16 line 2) =="
"$FX" verify tests/vectors/payload-f16.vec tests/vectors/payload-f32.vec tests/vectors/payload-f64.vec > "$OUT/fx-payload.log" 2>&1
echo "fx_payload_rc=$? $(grep -E '^total' "$OUT/fx-payload.log")"
grep '^FAIL' "$OUT/fx-payload.log" | head -5
echo "== fixed runner: audit gates (truth) =="
"$FX" verify "$SCR/out-audit/audit-payload-f16.vec" > "$OUT/fx-audit-payload.log" 2>&1
echo "fx_audit_payload_rc=$? $(grep -E '^total' "$OUT/fx-audit-payload.log")"
"$FX" verify "$SCR/out-audit/audit-minmax-sample.vec" "$SCR/out-audit/audit-seeded.vec" > "$OUT/fx-audit-minmax.log" 2>&1
echo "fx_audit_minmax_rc=$? $(grep -E '^total' "$OUT/fx-audit-minmax.log")"
echo "== c6 exact shape on fixed runner =="
"$FX" verify "$SCR/out-neg/ctrl/c6-good.vec" > "$OUT/fx-c6-good.log" 2>&1; echo "c6-good(fx) rc=$? $(grep -E '^total' "$OUT/fx-c6-good.log")"
"$FX" verify "$SCR/out-neg/ctrl/c6-bad.vec" > "$OUT/fx-c6-bad.log" 2>&1; echo "c6-bad(fx) rc=$? $(grep -E '^total' "$OUT/fx-c6-bad.log")"
echo "== header recheck (fixed ERE) =="
grep -cE 'msf(16|32|64)_(minimum|maximum)(_number|_magnitude|_magnitude_number)?\(msf(16|32|64)_t a, msf(16|32|64)_t b, msf_flags_t' include/muse_softfloat.h
grep -cE 'msf(16|32|64)_(get_payload|set_payload|set_payload_signaling)\(msf(16|32|64)_t a\)' include/muse_softfloat.h
echo "== MPFR finite corroboration =="
ls /c/msys64/mingw64/include/mpfr.h 2>/dev/null || echo "no mpfr header"
exit 0
