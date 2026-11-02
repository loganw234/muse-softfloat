#!/usr/bin/env bash
# 11_linuxprobe.sh - probe the actual (Linux) execution environment.
set -u
{
echo "== linux env probe =="
which python3 python gcc cc make awk 2>&1
python3 --version 2>&1
python3 -c "import mpmath; print('mpmath', mpmath.__version__)" 2>&1
python3 -c "import mpfr" 2>&1 | head -1
ls /usr/include/mpfr.h /usr/include/gmp.h 2>&1
ldconfig -p 2>/dev/null | grep -i -m5 "mpfr\|gmp" || echo "no ldconfig hits"
gcc -dumpmachine; gcc --version | head -1
echo "int main(){return 0;}" > /tmp/t.c && gcc /tmp/t.c -lmpfr -lgmp -o /tmp/t 2>&1 && echo "mpfr link OK" || echo "mpfr link FAIL"
grep -m1 -o "mpfr_exp2m1" /usr/include/mpfr.h 2>/dev/null || echo "no exp2m1 in header"
apt list --installed 2>/dev/null | grep -i -m5 mpfr || echo "apt query n/a"
} 2>&1 | tee "$(dirname "$0")/11_linuxprobe.log"
