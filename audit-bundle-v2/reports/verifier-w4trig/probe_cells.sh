#!/bin/bash
# Probe B: build copy sources + tiny direct caller; test settled zero-sign cells.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
cd "$ROOT" || exit 9
mkdir -p scratch/verifier-w4trig/tmp scratch/verifier-w4trig/out
cat > scratch/verifier-w4trig/tmp/cellprobe.c <<'EOF'
#include <stdio.h>
#include "muse_softfloat.h"
int main(void) {
    msf_flags_t fl = 0;
    struct { const char *op; int fmt; unsigned long long bits; } cases[] = {
        {"cos",16,0xb800ULL},{"cos",32,0xbf000000ULL},{"cos",64,0xbfe0000000000000ULL},
        {"cos",16,0x3800ULL},{"sin",16,0xbc00ULL},{"sin",32,0xbf800000ULL},{"sin",64,0xbff0000000000000ULL},
        {"sin",16,0xb800ULL},{"cos",16,0xb800ULL},
    };
    int rms[4] = {0,1,2,3};
    const char *rmn[4] = {"te","tz","tp","tn"};
    for (unsigned i = 0; i < sizeof(cases)/sizeof(cases[0]); i++) {
        for (int r = 0; r < 4; r++) {
            fl = 0;
            unsigned long long out = 0;
            if (cases[i].fmt == 16)
                out = (cases[i].op[0]=='c') ? msf16_cos_pi((msf16_t)cases[i].bits, rms[r], &fl)
                                            : msf16_sin_pi((msf16_t)cases[i].bits, rms[r], &fl);
            else if (cases[i].fmt == 32)
                out = (cases[i].op[0]=='c') ? msf32_cos_pi((msf32_t)cases[i].bits, rms[r], &fl)
                                            : msf32_sin_pi((msf32_t)cases[i].bits, rms[r], &fl);
            else
                out = (cases[i].op[0]=='c') ? msf64_cos_pi(cases[i].bits, rms[r], &fl)
                                            : msf64_sin_pi(cases[i].bits, rms[r], &fl);
            printf("%s f%-3d in=%llx rm=%s out=%llx flags=%x\n",
                   cases[i].op, cases[i].fmt, cases[i].bits, rmn[r], out, fl);
        }
    }
    return 0;
}
EOF
gcc -std=c11 -O2 -Wall -Wextra -ffp-contract=off -Wno-error \
  -Iworktrees/verify4-trig/include scratch/verifier-w4trig/tmp/cellprobe.c \
  worktrees/verify4-trig/src/msf16.c worktrees/verify4-trig/src/msf32.c \
  worktrees/verify4-trig/src/msf64.c worktrees/verify4-trig/src/msf_flags.c \
  worktrees/verify4-trig/src/msf_wide.c worktrees/verify4-trig/src/msf_roundpack.c \
  worktrees/verify4-trig/src/msf_string.c worktrees/verify4-trig/src/msf_math.c \
  -o scratch/verifier-w4trig/tmp/cellprobe.exe 2>&1 | head -20
echo "build rc=$?"
scratch/verifier-w4trig/tmp/cellprobe.exe
