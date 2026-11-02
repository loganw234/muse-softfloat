#!/usr/bin/env bash
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
bash "$WS/softfloat-bootstrap-kit/tools/ledger.sh" append "$WS/ledger" parcel-w6examples \
  "w6-examples tip b6e08fd: host+pico on-ramp, standard PASS, UF2 built not flashed" \
  < "$WS/scratch/parcel-w6examples/ledger_body.txt"
