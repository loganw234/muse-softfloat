#!/usr/bin/env bash
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
LIVE=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6sanitize/live
mkdir -p "$LIVE/toolcheck"
cd "$LIVE/toolcheck" || exit 9
cat > oadd.c <<'EOF'
#include <limits.h>
#include <stdio.h>
int main(int argc, char **argv) {
    (void)argv;
    volatile int x = INT_MAX;
    int y = x + argc;
    printf("OADD %d\n", y);
    return 0;
}
EOF
cat > oshift.c <<'EOF'
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    int sh = (argc > 1) ? atoi(argv[1]) : 40;
    volatile unsigned int v = 1u;
    unsigned int y = v << sh;
    printf("OSHIFT %u\n", y);
    return 0;
}
EOF
gcc -std=c11 -O2 -fsanitize-undefined-trap-on-error oadd.c -o oadd-traperr.exe 2> oadd-build.log || { echo "oadd build fail"; cat oadd-build.log; }
./oadd-traperr.exe > oadd.log 2>&1
echo "oadd traperr: rc=$? out=[$(cat oadd.log)]"
gcc -std=c11 -O2 -fsanitize=undefined oshift.c -o oshift-ubsan.exe 2> oshift-build.log || { echo "oshift ubsan build rc=$?"; cat oshift-build.log; }
ls -la oshift-ubsan.exe 2>/dev/null || echo "oshift-ubsan.exe missing (link fail as expected?)"
gcc -std=c11 -O2 -fsanitize-undefined-trap-on-error oshift.c -o oshift-traperr.exe 2> oshift2-build.log || { echo "oshift traperr build fail"; cat oshift2-build.log; }
./oshift-traperr.exe 40 > oshift.log 2>&1
echo "oshift traperr: rc=$? out=[$(cat oshift.log)]"
gcc --help=sanitizers 2>/dev/null | head -20
