#!/usr/bin/env bash
# 15-hextie.sh - hand-tie from_hex probe: kernel ta correctness vs the
# reference's ta arm on a genuine binary midpoint.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
V="$SCRATCH"
mkdir -p "$V/tmp/hextie"
export TMPDIR="$V/tmp" TMP="$V/tmp" TEMP="$V/tmp"
printf '%s\n' \
  "msf16_from_hex te IN=0x801p-11 -> 3c00 10 C=9 hand-tie" \
  "msf16_from_hex ta IN=0x801p-11 -> 3c01 10 C=9 hand-tie" \
  > "$V/tmp/hextie/tie.vec"
"$V/tmp/self/runner.exe" verify "$V/tmp/hextie/tie.vec" > "$V/tmp/hextie/tie.log" 2>&1
echo "hand-tie replay exit: $?"
grep -E "^(total|VERDICT)" "$V/tmp/hextie/tie.log"
grep "^FAIL" "$V/tmp/hextie/tie.log" || true
"$MSF_PYTHON" - "$COPY/tests" <<'PYEOF'
import sys
sys.path.insert(0,sys.argv[1])
import gen_vectors_str as g
for rm in ("te","ta","tz"):
    print(rm, [hex(x) for x in g.from_hex_ref("0x801p-11",rm,"f16")])
PYEOF
