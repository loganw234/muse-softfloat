#!/usr/bin/env bash
# 104_s5cell.sh - targeted smallest-repro of the S5 mismatch (no full rerun).
set -u
D="$(dirname "$0")"
"$D/build/vdriver.exe" f32 C3160000 C3160001 2>&1 | tee "$D/104_s5cell.log"
