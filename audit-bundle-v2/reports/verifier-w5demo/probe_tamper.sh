#!/usr/bin/env bash
export MSF_PYTHON=python
F=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5demo/fresh
A="$F/demo/cache/archives/rebound-262a9cce102c69ca2cf7f3c6c1264e5e60002b7d.tar.gz"
cp "$A" /tmp/rebound-good.tgz
python3flip() { MSF_PYTHON=python python "$@"; }
python "$F/demo/make_ias15_extract.py" --help >/dev/null 2>&1
python - "$A" <<'EOF'
import sys
p = sys.argv[1]
d = open(p, 'rb').read()
open(p, 'wb').write(d[:100] + bytes([d[100] ^ 1]) + d[101:])
print('flipped one bit at offset 100')
EOF
cd "$F" && bash demo/fetch.sh --offline > /tmp/probeB.log 2>&1; echo "PROBE_B_EXIT=$?"
cat /tmp/probeB.log
cp /tmp/rebound-good.tgz "$A"
cd "$F" && bash demo/fetch.sh --offline > /tmp/probeB2.log 2>&1; echo "RESTORE_EXIT=$?"
tail -2 /tmp/probeB2.log
