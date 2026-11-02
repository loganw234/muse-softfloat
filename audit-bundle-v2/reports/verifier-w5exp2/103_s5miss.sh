#!/usr/bin/env bash
# 103_s5miss.sh - confirm the S5 mismatch is the known E_tie cell.
set -u
D="$(dirname "$0")"
grep "MISMATCH" "$D/70_f32shards.log" > "$D/103_s5miss.txt" 2>&1 || true
cat "$D/103_s5miss.txt"
