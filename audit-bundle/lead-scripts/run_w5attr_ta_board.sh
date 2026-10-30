#!/usr/bin/env bash
# Lead: ta-rich sampled board replay for SF-2 Step 1.
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
WS="$(cd .. && pwd)"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export MSF_BOARD_SERIAL=E66440A2CB6F5C2B
export MSF_BOARD_PORT=COM8
source board/common.sh
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
OUT="$WS/scratch/lead/w5attr-ta"
mkdir -p "$OUT"
"$MSF_PYTHON" - "$OUT/ta-sample.vec" <<'PYEOF'
import glob, sys
out = sys.argv[1]
lines = []
for p in sorted(glob.glob("tests/vectors/*.vec")):
    with open(p, encoding="utf-8") as f:
        for line in f:
            if " ta " in line and not line.startswith("internal.") and "IN=" not in line and "OUT=" not in line:
                lines.append(line.rstrip("\n"))
sample = lines[::37]
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(sample) + "\n")
print("public ta total", len(lines), "sampled stride37", len(sample))
PYEOF
[ -s "$OUT/ta-sample.vec" ] || board_fail "ta sample empty"
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
    src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c \
    src/msf_roundpack.c src/msf_string.c src/msf_math.c \
    tests/runner.c tests/sha256.c -o "$BOARD_BUILD/msf_runner.exe" \
    > "$OUT/host-build.log" 2>&1 || board_fail "host runner build"
"$BOARD_BUILD/msf_runner.exe" verify "$OUT/ta-sample.vec" > "$OUT/host-verify.log" 2>&1 || { cat "$OUT/host-verify.log"; board_fail "host verify"; }
"$BOARD_BUILD/msf_runner.exe" hash "$OUT/ta-sample.vec" > "$OUT/host-hash.log" 2>&1 || board_fail "host hash"
EXPECT_SHA=$(grep '^whole-run-sha256' "$OUT/host-hash.log" | awk '{print $2}')
echo "host: $(grep -E '^(total|VERDICT)' "$OUT/host-verify.log") sha256=$EXPECT_SHA"
take_lock "SF-2 Step 1 ta-rich sampled replay"
flash_uf2 "$BOARD_BUILD/fw/msf_board_harness.uf2"
$PY board/host_replay.py --port "$MSF_BOARD_PORT" "$OUT/ta-sample.vec" --expect-sha256 "$EXPECT_SHA" \
    > "$OUT/replay.log" 2>&1 || { cat "$OUT/replay.log"; board_fail "ta board replay"; }
cat "$OUT/replay.log"
echo "ta board replay: PASS"
