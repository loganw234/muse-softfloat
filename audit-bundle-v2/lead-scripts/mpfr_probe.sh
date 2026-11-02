#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/lead || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR=$PWD/tmp
export TMP="$(cygpath -w "$TMPDIR")" TEMP="$(cygpath -w "$TMPDIR")"
cat > mpfr_probe.c <<'EOF'
#include <stdio.h>
#include <mpfr.h>
int main(void) {
    mpfr_t x;
    mpfr_init2(x, 200);
    mpfr_set_ui(x, 3, MPFR_RNDN);
    mpfr_sqrt(x, x, MPFR_RNDN);
    printf("MPFR %s sqrt(3)@200b=", mpfr_get_version());
    mpfr_out_str(stdout, 10, 25, x, MPFR_RNDN);
    printf("\n");
    mpfr_clear(x);
    return 0;
}
EOF
gcc -std=c11 -O2 mpfr_probe.c -lmpfr -lgmp -o mpfr_probe.exe && ./mpfr_probe.exe
echo "mpfr rc=$?"
date '+now %Y-%m-%dT%H:%M:%S%z'
ls ~/.local/share/muse/sessions/2026/10/26/01a17907-4147-7333-a565-56071da9d971/ 2>/dev/null | head
ls ~/.local/share/muse/sessions/2026/10/26/ | head -30
