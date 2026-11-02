#!/usr/bin/env bash
# Probe 7b prep2: size the snapshot, check for cft names, check smoke func inputs.
set -euo pipefail
cd "C:/Users/logan/source/repos/Muse-Softfloat"
echo "--- sizes ---"
du -sh muse-softfloat/src muse-softfloat/include muse-softfloat/tables muse-softfloat/tests muse-softfloat/tools muse-softfloat/board muse-softfloat/compat 2>/dev/null
echo "--- cft names anywhere in snapshot (names only, never opened) ---"
find muse-softfloat -iname '*cft*' | head -10 || true
echo "--- build/smoke state ---"
ls -la muse-softfloat/build/ | head; ls muse-softfloat/build/smoke 2>/dev/null | head -5 || echo "(no build/smoke dir)"
echo "--- smoke() body ---"
sed -n '/^smoke()/,/^}/p' muse-softfloat/tools/run.sh
