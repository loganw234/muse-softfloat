#!/usr/bin/env bash
# 13_gmpcheck.sh - can we compile against mpfr.h (needs gmp.h)?
set -u
D="$(dirname "$0")"
{
echo '#include <mpfr.h>
int main(void){ mpfr_t x; mpfr_init2(x, 128); mpfr_clear(x); return 0; }' > "$D/probe_mpfr.c"
gcc -std=c11 -O2 "$D/probe_mpfr.c" -lmpfr -lgmp -o "$D/probe_mpfr.exe" 2>&1 && echo "COMPILE+LINK OK" || echo "COMPILE FAIL"
find / -name "gmp.h" -not -path "*/proc/*" 2>/dev/null | head -5
ls /usr/include/ | grep -i -m10 "gmp\|mpfr" || true
} 2>&1 | tee "$D/13_gmpcheck.log"
