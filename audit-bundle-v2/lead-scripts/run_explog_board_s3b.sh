#!/usr/bin/env bash
# Lead: explog sampled board replay after Step 3b (exp+log surface).
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
WS="$(cd .. && pwd)"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export MSF_BOARD_SERIAL=E66440A2CB6F5C2B
export MSF_BOARD_PORT=COM8
source board/common.sh
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
OUT="$WS/scratch/lead/explog-board-s3b"
mkdir -p "$OUT"
"$MSF_PYTHON" - "$OUT/explog-sample.vec" <<'PYEOF'
import sys
out = sys.argv[1]
lines = []
for f in ("tests/vectors/explog-f16.vec", "tests/vectors/explog-f32.vec", "tests/vectors/explog-f64.vec"):
    with open(f, encoding="utf-8") as fh:
        lines += [l.rstrip("\n") for l in fh if l.strip() and not l.startswith("#")]
sample = lines[::41]
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(sample) + "\n")
ops = {}
for l in sample:
    ops[l.split()[0]] = ops.get(l.split()[0], 0) + 1
print("explog total", len(lines), "sampled stride41", len(sample))
print("sample op census:", dict(sorted(ops.items())))
PYEOF
[ -s "$OUT/explog-sample.vec" ] || board_fail "sample empty"
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
    src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c \
    tests/runner.c tests/sha256.c -o "$BOARD_BUILD/msf_runner.exe" \
    > "$OUT/host-build.log" 2>&1 || { tail -20 "$OUT/host-build.log"; board_fail "host runner build"; }
"$BOARD_BUILD/msf_runner.exe" verify "$OUT/explog-sample.vec" > "$OUT/host-verify.log" 2>&1 || { cat "$OUT/host-verify.log"; board_fail "host verify"; }
"$BOARD_BUILD/msf_runner.exe" hash "$OUT/explog-sample.vec" > "$OUT/host-hash.log" 2>&1 || board_fail "host hash"
EXPECT_SHA=$(grep '^whole-run-sha256' "$OUT/host-hash.log" | awk '{print $2}')
echo "host: $(grep -E '^(total|VERDICT)' "$OUT/host-verify.log") sha256=$EXPECT_SHA"
take_lock "SF-2 Step 3b explog sampled replay"
build_fw fw
flash_uf2 "$BOARD_BUILD/fw/msf_board_harness.uf2"
$PY board/host_replay.py --port "$MSF_BOARD_PORT" "$OUT/explog-sample.vec" --expect-sha256 "$EXPECT_SHA" \
    > "$OUT/replay.log" 2>&1 || { cat "$OUT/replay.log"; board_fail "explog board replay"; }
cat "$OUT/replay.log"
sha256sum "$BOARD_BUILD/fw/msf_board_harness.uf2"
echo "explog s3b board replay: PASS"
