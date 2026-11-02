#!/bin/bash
# Probe O3: direct targeted kernel calls - copy vs mutants on same inputs.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
cd "$ROOT" || exit 9
cat > $V/tmp/tcall.c <<'EOF'
#include <stdio.h>
#include "muse_softfloat.h"
int main(void) {
    /* argv-free: fixed probes. B: sin f16 0x3400 all modes (want +0.7071: 0x39a8-ish).
       C: sin f16 0x3556 all modes (directed spread). */
    unsigned short xs[2] = {0x3400, 0x3556};
    for (int k = 0; k < 2; k++) {
        for (int rm = 0; rm < 4; rm++) {
            msf_flags_t fl = 0;
            msf16_t got = msf16_sin_pi((msf16_t)xs[k], rm, &fl);
            printf("sin f16 %04x rm=%d -> %04x/%02x\n", xs[k], rm, got, fl);
        }
    }
    return 0;
}
EOF
for tag in copy signfix mutB mutC; do
  case $tag in
    copy) S=$ROOT/worktrees/verify4-trig;;
    *) S=$V/$tag;;
  esac
  [ $tag = signfix ] && S=$V/signfix
  gcc -std=c11 -O2 -ffp-contract=off -Wno-error -I$S/include \
    $V/tmp/tcall.c $S/src/msf16.c $S/src/msf32.c $S/src/msf64.c \
    $S/src/msf_flags.c $S/src/msf_wide.c $S/src/msf_roundpack.c \
    $S/src/msf_string.c $S/src/msf_math.c -o $V/tmp/tcall_$tag.exe 2>/dev/null
  echo "== $tag =="
  $V/tmp/tcall_$tag.exe
done
echo "== harness decide (MPFR truth) =="
printf 'msf16_sin_pi 3400\nmsf16_sin_pi 3556\n' | $V/tmp/trigx.exe decide
