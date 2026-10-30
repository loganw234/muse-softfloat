#!/usr/bin/env bash
# Lead: alg-rich sampled board replay (stride sample of committed alg vecs).
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
WS="$(cd .. && pwd)"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export MSF_BOARD_SERIAL=E66440A2CB6F5C2B
export MSF_BOARD_PORT=COM8
source board/common.sh
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
OUT="$WS/scratch/lead/alg-board"
mkdir -p "$OUT"
"$MSF_PYTHON" - "$OUT/alg-sample.vec" <<'PYEOF'
import sys
out = sys.argv[1]
lines = []
for f in ("tests/vectors/alg-f16.vec", "tests/vectors/alg-f32.vec", "tests/vectors/alg-f64.vec"):
    with open(f, encoding="utf-8") as fh:
        lines += [l.rstrip("\n") for l in fh if l.strip() and not l.startswith("#")]
sample = lines[::7]
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(sample) + "\n")
print("alg total", len(lines), "sampled stride7", len(sample))
PYEOF
[ -s "$OUT/alg-sample.vec" ] || board_fail "sample empty"
"$BOARD_BUILD/msf_runner.exe" verify "$OUT/alg-sample.vec" > "$OUT/host-verify.log" 2>&1 || { cat "$OUT/host-verify.log"; board_fail "host verify"; }
"$BOARD_BUILD/msf_runner.exe" hash "$OUT/alg-sample.vec" > "$OUT/host-hash.log" 2>&1 || board_fail "host hash"
EXPECT_SHA=$(grep '^whole-run-sha256' "$OUT/host-hash.log" | awk '{print $2}')
echo "host: $(grep -E '^(total|VERDICT)' "$OUT/host-verify.log") sha256=$EXPECT_SHA"
take_lock "SF-2 algebraic sampled replay"
flash_uf2 "$BOARD_BUILD/fw/msf_board_harness.uf2"
$PY board/host_replay.py --port "$MSF_BOARD_PORT" "$OUT/alg-sample.vec" --expect-sha256 "$EXPECT_SHA" \
    > "$OUT/replay.log" 2>&1 || { cat "$OUT/replay.log"; board_fail "alg board replay"; }
cat "$OUT/replay.log"
echo "alg board replay: PASS"
