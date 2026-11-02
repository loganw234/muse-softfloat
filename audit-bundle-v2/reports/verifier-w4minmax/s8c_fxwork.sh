#!/usr/bin/env bash
# verifier-w4minmax s8c: fixed runner under a repo-mirroring scratch tree.
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-minmax
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4minmax
OUT=$SCR/out-fixed
W=$OUT/fxwork
rm -rf "$W"
mkdir -p "$W/src" "$W/include" "$W/tests"
cp "$COPY/src/"*.c "$COPY/src/"*.h "$COPY/src/"*.inc "$W/src/"
cp "$COPY/include/muse_softfloat.h" "$W/include/"
cp "$COPY/tests/runner.c" "$COPY/tests/sha256.c" "$COPY/tests/sha256.h" "$COPY/tests/msf_dispatch.h" "$W/tests/"
cp "$COPY/src/msf_formats.h" "$W/src/"
F="$W/src/msf_performat.inc"
sed -i 's/return a->sign ? 1 : -1; \/\* -0 below +0 (9.6) \*\//return a->sign ? -1 : 1; \/* -0 below +0 (9.6) *\//' "$F"
sed -i 's/if ((an ? da.cls : db.cls) == MSF_VC_QUIET_NAN)/if ((an ? da.cls : db.cls) == MSF_VC_SIGNALING_NAN)/' "$F"
sed -i 's/(signaling ? MSF_PF_C(QUIET_BIT) : 0u)/(signaling ? 0u : MSF_PF_C(QUIET_BIT))/' "$F"
diff "$COPY/src/msf_performat.inc" "$F"
export PATH=/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH
cd "$W" || exit 9
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -DMSF_BUILD_ID='"fixed-experiment"' src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c tests/runner.c tests/sha256.c -o fx_runner.exe 2>"$OUT/fx-build2.log"
echo "fx_build_rc=$?"
tail -3 "$OUT/fx-build2.log"
FX="$W/fx_runner.exe"
cd "$COPY" || exit 9
echo "== fixed: committed minmax =="
"$FX" verify tests/vectors/minmax-f16.vec tests/vectors/minmax-f32.vec tests/vectors/minmax-f64.vec > "$OUT/fx-minmax.log" 2>&1
echo "rc=$? $(grep -E '^total' "$OUT/fx-minmax.log")"
echo "== fixed: committed payload UNFIXED =="
"$FX" verify tests/vectors/payload-f16.vec tests/vectors/payload-f32.vec tests/vectors/payload-f64.vec > "$OUT/fx-payload.log" 2>&1
echo "rc=$? $(grep -E '^total' "$OUT/fx-payload.log")"
grep '^FAIL' "$OUT/fx-payload.log" | head -5
echo "== fixed: audit truth gates =="
"$FX" verify "$SCR/out-audit/audit-payload-f16.vec" > "$OUT/fx-audit-payload.log" 2>&1
echo "rc=$? $(grep -E '^total' "$OUT/fx-audit-payload.log")"
"$FX" verify "$SCR/out-audit/audit-minmax-sample.vec" "$SCR/out-audit/audit-seeded.vec" > "$OUT/fx-audit-minmax.log" 2>&1
echo "rc=$? $(grep -E '^total' "$OUT/fx-audit-minmax.log")"
echo "== fixed: c6 exact shape =="
"$FX" verify "$SCR/out-neg/ctrl/c6-good.vec" > "$OUT/fx-c6-good.log" 2>&1; echo "good rc=$? $(grep -E '^total' "$OUT/fx-c6-good.log")"
"$FX" verify "$SCR/out-neg/ctrl/c6-bad.vec" > "$OUT/fx-c6-bad.log" 2>&1; echo "bad rc=$? $(grep -E '^total' "$OUT/fx-c6-bad.log")"
exit 0
