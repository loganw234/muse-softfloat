#!/usr/bin/env bash
# verifier-w4minmax s9: final structural checks + MPFR corroboration.
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-minmax
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4minmax
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
OUT=$SCR/out-final
mkdir -p "$OUT"
cd "$COPY" || exit 9
echo "== TU includes =="
grep -n 'msf_performat.inc\|MSF_PF' src/msf16.c src/msf32.c src/msf64.c | head -12
echo "== minmax/payload defs outside the .inc? =="
grep -n 'minimum\|payload' src/msf16.c src/msf32.c src/msf64.c | grep -v '^.*include' | head -10
echo "(none above = all Tier 2 logic lives in the owned .inc)"
echo "== dispatch diff review (mechanical?) =="
git diff 8578114 HEAD -- tests/msf_dispatch.h | head -60
echo "== copy tree clean (no modifications by verifier)? =="
git status --short | head -10
echo "status-lines=$(git status --short | wc -l)"
echo "== MPFR corroboration: Number-form finite value selection =="
export PATH=/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH
cat > "$OUT/mpfr_minmax.c" <<'EOF'
#include <stdio.h>
#include <mpfr.h>
/* Corroborate 9.6 Number-form VALUE selection on finite/zero/inf only.
   NaN/flags/payloads are out of scope for MPFR (no sNaN, other flag model). */
static void show(const char *a, const char *b, int prec) {
    mpfr_t x, y, r;
    mpfr_inits2(prec, x, y, r, (mpfr_ptr)0);
    mpfr_set_str(x, a, 10, MPFR_RNDN);
    mpfr_set_str(y, b, 10, MPFR_RNDN);
    mpfr_exp_t e; char *s;
    mpfr_min(r, x, y, MPFR_RNDN);
    s = mpfr_get_str(NULL, &e, 10, 0, r, MPFR_RNDN);
    printf("prec=%d min(%s,%s) = 0.%se%ld", prec, a, b, s, (long)e);
    mpfr_free_str(s);
    printf(" sign=%d", mpfr_signbit(r));
    mpfr_max(r, x, y, MPFR_RNDN);
    s = mpfr_get_str(NULL, &e, 10, 0, r, MPFR_RNDN);
    printf(" | max = 0.%se%ld sign=%d\n", s, (long)e, mpfr_signbit(r));
    mpfr_free_str(s);
    mpfr_clears(x, y, r, (mpfr_ptr)0);
}
int main(void) {
    printf("mpfr %s\n", mpfr_get_version());
    show("-0", "0", 11); show("-0", "0", 24); show("-0", "0", 53);
    show("-1", "1", 24); show("2", "1.5", 53);
    show("-1e30", "-1e-30", 24); show("1e30", "inf", 53);
    return 0;
}
EOF
gcc -std=c11 -O2 -Wall "$OUT/mpfr_minmax.c" -o "$OUT/mpfr_minmax.exe" -lmpfr -lgmp 2>"$OUT/mpfr-build.log"
echo "mpfr_build_rc=$?"
cat "$OUT/mpfr-build.log" | head -5
"$OUT/mpfr_minmax.exe"
exit 0
