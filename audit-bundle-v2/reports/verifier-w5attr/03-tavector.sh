#!/usr/bin/env bash
# 03-tavector.sh - trace one ta vector end to end by reading
# gen_tables/header/runner/dispatch (text line -> public enum ->
# internal mode -> pack arm). Uses the first ta line of a committed file.
set -u
echo "== public enum (generated header, copy) =="
grep -n -A7 "typedef enum msf_rounding" "$COPY/include/muse_softfloat.h"
echo "== generator prelude (copy) =="
grep -n -A7 "typedef enum msf_rounding" "$COPY/tools/gen_tables.py"
echo "== runner token (copy tests/runner.c) =="
grep -n "ta" "$COPY/tests/runner.c" | head -n 5
echo "== dispatch pass-through (copy tools/gen_tables.py wrapper_for) =="
grep -n "msf_rounding_t" "$COPY/tools/gen_tables.py"
echo "== dispatched call for one op (copy tests/msf_dispatch.h) =="
grep -n "msf_call_msf32_add" "$COPY/tests/msf_dispatch.h" | head -n 3
echo "== internal mode (copy src/msf_internal.h) =="
grep -n -A8 "Internal rounding modes" "$COPY/src/msf_internal.h"
echo "== pack arm (copy src/msf_roundpack.c) =="
sed -n '51,67p;116,122p' "$COPY/src/msf_roundpack.c"
echo "== one committed ta line traced =="
grep -m1 -n " ta " "$COPY/tests/vectors/arith-f32.vec"
echo "== enum agreement check =="
gen_val=$(grep -A6 "typedef enum msf_rounding" "$COPY/tools/gen_tables.py" | grep TIES_TO_AWAY | grep -o "[0-9]*")
hdr_val=$(grep -A6 "typedef enum msf_rounding" "$COPY/include/muse_softfloat.h" | grep TIES_TO_AWAY | grep -o "[0-9]*")
int_val=$(grep "MSF_IROUND_TIES_TO_AWAY" "$COPY/src/msf_internal.h" | grep -o "[0-9]*")
echo "gen_tables=$gen_val header=$hdr_val internal=$int_val"
if [ "$gen_val" = "$hdr_val" ] && [ "$hdr_val" = "$int_val" ]; then echo "ENUM TRACE: AGREE"; else echo "ENUM TRACE: DISAGREE"; fi
