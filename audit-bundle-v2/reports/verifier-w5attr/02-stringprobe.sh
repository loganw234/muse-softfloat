#!/usr/bin/env bash
# 02-stringprobe.sh - probe the study's two string cases + sign and
# below-half discriminators with our own harness (copy kernel only).
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
V="$SCRATCH"
mkdir -p "$V/tmp"
export TMPDIR="$V/tmp" TMP="$V/tmp" TEMP="$V/tmp"
cat > "$V/tmp/str_probe.c" <<'EOF'
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "muse_softfloat.h"
int main(void) {
    char buf[128];
    msf_flags_t fl = 0;
    msf_decimal_spec_t d1 = {1, MSF_DECIMAL_STYLE_SCIENTIFIC, 0};
    msf_decimal_spec_t d3 = {3, MSF_DECIMAL_STYLE_SCIENTIFIC, 0};
    msf_hex_spec_t h2 = {2};
    int fails = 0;
#define CHECK(got, want) do { if (strcmp(got, want) != 0) { printf("  MISMATCH (want %s)\n", want); fails++; } } while (0)
    fl = 0;
    msf64_to_decimal(0x4004000000000000ull, &d1, buf, sizeof buf, MSF_ROUND_TIES_TO_AWAY, &fl);
    printf("to_decimal(2.5,prec=1,ta) = %s flags=%02x\n", buf, fl);
    CHECK(buf, "3e+00");
    fl = 0;
    msf32_to_hex(0x3F808000u, &h2, buf, sizeof buf, MSF_ROUND_TIES_TO_AWAY, &fl);
    printf("to_hex(1+2^-9 f32,prec=2,ta) = %s flags=%02x\n", buf, fl);
    CHECK(buf, "0x1.01p+0");
    fl = 0;
    msf64_to_decimal(0x4004000000000000ull, &d3, buf, sizeof buf, MSF_ROUND_TIES_TO_AWAY, &fl);
    printf("to_decimal(2.5,prec=3,ta) = %s flags=%02x\n", buf, fl);
    CHECK(buf, "2.50e+00");
    fl = 0;
    msf64_to_decimal(0xC004000000000000ull, &d1, buf, sizeof buf, MSF_ROUND_TIES_TO_AWAY, &fl);
    printf("to_decimal(-2.5,prec=1,ta) = %s flags=%02x\n", buf, fl);
    CHECK(buf, "-3e+00");
    /* beyond-H digit tie: 21 sig digits, dropped == 5 exactly, kept even.
     * Two-step semantics: H-step only; both modes must pack to 2.5. */
    {
        const char *s = "2.50000000000000000005";
        size_t c1 = 0, c2 = 0;
        msf_flags_t f1 = 0, f2 = 0;
        msf64_t b_te = msf64_from_decimal(s, &c1, MSF_ROUND_TIES_TO_EVEN, &f1);
        msf64_t b_ta = msf64_from_decimal(s, &c2, MSF_ROUND_TIES_TO_AWAY, &f2);
        printf("from_decimal(%s): te=%016llx fl=%02x ta=%016llx fl=%02x\n",
               s, (unsigned long long)b_te, f1, (unsigned long long)b_ta, f2);
        if (b_te != 0x4004000000000000ull || b_ta != 0x4004000000000000ull) {
            printf("  MISMATCH (want both 2.5 bits)\n"); fails++;
        }
    }
    printf(fails ? "STRING PROBE: %d MISMATCHES\n" : "STRING PROBE: ALL MATCH\n", fails);
    return fails ? 1 : 0;
}
EOF
/c/msys64/mingw64/bin/gcc -std=c11 -O2 -Wall -Wextra -Werror -I"$COPY/include" -I"$COPY/src" \
  "$V/tmp/str_probe.c" "$COPY"/src/*.c -o "$V/tmp/str_probe.exe" 2>"$V/tmp/str_probe.build.log" \
  || { cat "$V/tmp/str_probe.build.log"; echo "BUILD FAIL"; exit 1; }
"$V/tmp/str_probe.exe"
