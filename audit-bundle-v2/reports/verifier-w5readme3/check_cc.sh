#!/usr/bin/env bash
set -u
export PATH=/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH
which gcc
gcc -dumpmachine
gcc -dumpversion
cat > /tmp/probe_fem.c <<'EOF'
#include <stdio.h>
int main(void){ printf("FLT_EVAL_METHOD=%d\n", __FLT_EVAL_METHOD__); return 0; }
EOF
gcc -std=c11 /tmp/probe_fem.c -o /tmp/probe_fem.exe && /tmp/probe_fem.exe
