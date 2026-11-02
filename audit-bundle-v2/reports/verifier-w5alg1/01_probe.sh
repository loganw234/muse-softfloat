#!/usr/bin/env bash
# 01_probe.sh - compile copy sources + tiny driver, call rSqrt on a few inputs.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-alg1
OUT=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5alg1/out
MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
mkdir -p "$OUT"
cd "$COPY" || exit 9
cat > "$OUT/probe_rsqrt.c" <<'EOF'
#include <stdio.h>
#include "muse_softfloat.h"
int main(void) {
    /* modes: print enum values used by runner: te tz tp tn ta order unknown; use ints 0..4 */
    uint16_t inputs[] = {0x3c00u, 0x4000u, 0x0001u, 0x0000u, 0x8000u, 0x7c00u};
    int m;
    size_t i;
    for (i = 0; i < sizeof(inputs)/sizeof(inputs[0]); i++) {
        for (m = 0; m < 5; m++) {
            msf_flags_t fl = 0;
            msf16_t r = msf16_r_sqrt((msf16_t)inputs[i], (msf_rounding_t)m, &fl);
            printf("in=%04x mode=%d -> %04x flags=%02x\n", inputs[i], m, (unsigned)r, (unsigned)fl);
        }
    }
    return 0;
}
EOF
gcc -std=c11 -O2 -ffp-contract=off -Iinclude \
  src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c \
  src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c \
  "$OUT/probe_rsqrt.c" -o "$OUT/probe_rsqrt.exe" 2>"$OUT/probe_build.log" \
  || { cat "$OUT/probe_build.log"; exit 1; }
"$OUT/probe_rsqrt.exe"
