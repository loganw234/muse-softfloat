#!/bin/bash
# rerun_quick.sh - re-run the fast reproductions behind REPORT.md (about 30 s). Everything stays inside $A.
# Not included (slow, see REPORT.md "Method"): the 3-minute full-history blob scan (hist/scan_blobs.py).
set -u
A=/tmp/claude-0/-home-user-muse-softfloat/f663923d-ec02-5a9b-9be5-2326751bedd2/scratchpad/agents/security-code
cd "$A"

echo "== SC-2/SC-3/SC-4: demo/fetch.py black-box experiments (synthetic archives, file:// URLs, no network)"
python3 -I -B fetchtest/fetch_experiments.py "$A/repo/demo/fetch.py" "$A/fetchtest/work" 2>&1 | grep -E '^E[0-9]|tree file after|escape.txt'
python3 -I -B fetchtest/redirect_check.py 2>&1 | head -4

echo "== SC-1: ASan reproductions (binaries built by the commands in REPORT.md)"
( cd repro && ./runner_asan hash evil.vec 2>&1 | grep -E 'ERROR: AddressSanitizer|WRITE of size|hash_result' | head -3 )
( cd repro && ./harness_host_asan < attack.txt 2>&1 | grep -E 'ERROR: AddressSanitizer|WRITE of size|hash_result' | head -3 )

echo "== SC-5/SC-6: committed wasm vs fresh HEAD build (differential) and embedded paths"
node hist/wasm/diffwasm.mjs hist/wasm/msf_head.wasm hist/wasm/msf_fresh.wasm 200
python3 -I -B hist/wasmsec.py hist/wasm/msf_head.wasm | head -3
strings -a -n 8 hist/wasm/msf_head.wasm | grep -c 'Users.logan'

echo "== SC-7: board.lock race (24 simultaneous callers of the verbatim take_lock; a correct lock gives exactly 1)"
( cd locktest && for r in 1 2 3; do rm -f ledger/board.lock; for i in $(seq 1 24); do ./worker.sh "$A/locktest/ledger" "$A/locktest/lockfns.sh" & done > round.out 2>&1; wait; echo "round $r: holders=$(grep -c '^WON' round.out)"; done ) 2>/dev/null

echo "== SC-8: verbatim symbol_scan() with and without nm"
( cd gatetest && ./drive.sh x "$A/gatetest/bin_no_nm" nonm 2>&1 | tail -3 )
