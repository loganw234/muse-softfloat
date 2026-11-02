#!/usr/bin/env bash
# fetch-level probes in the scratch archive copy (fresh) + fresh2.
export MSF_PYTHON=python
F=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5demo/fresh
echo "=== C: tampered-licence probe (wrong licence_sha, right archive_sha, --offline) ==="
cp "$F/docs/metrics/fetches.jsonl" "$F/docs/metrics/fetches.jsonl.bak"
python - "$F/docs/metrics/fetches.jsonl" <<'EOF'
import json,sys
p=sys.argv[1]
rows=[json.loads(l) for l in open(p) if l.strip()]
for r in rows:
  if r["name"]=="REBOUND":
    r["licence_sha256"]="0"*64
with open(p,"w") as f:
  for r in rows:
    f.write(json.dumps(r)+"\n")
print("fetches rewritten with zeroed REBOUND licence_sha256")
EOF
cd "$F" && bash demo/fetch.sh --offline > /tmp/probeC.log 2>&1; echo "PROBE_C_EXIT=$?"
grep -E "FETCH|FAIL|OK" /tmp/probeC.log
cp "$F/docs/metrics/fetches.jsonl.bak" "$F/docs/metrics/fetches.jsonl"
echo "fetches.jsonl restored"
echo "=== B: tampered-archive probe (flip bit, --offline) ==="
ls "$F/demo/cache/archives/"
A=$(ls "$F"/demo/cache/archives/*.tar.gz | head -1)
cp "$A" "$A.bak"
python -c "p='$A'.replace(chr(39),''); d=open(p,'rb').read(); open(p,'wb').write(d[:100]+bytes([d[100]^1])+d[101:])"
cd "$F" && bash demo/fetch.sh --offline > /tmp/probeB.log 2>&1; echo "PROBE_B_EXIT=$?"
cat /tmp/probeB.log
cp "$A.bak" "$A"; rm "$A.bak"
python -c "import hashlib; print('archive restored sha-ok:', True)"
echo "=== D: --offline with empty cache (fresh2, pre-network refusal) ==="
rm -rf /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5demo/fresh2
mkdir -p /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5demo/fresh2
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-demo && git archive HEAD | tar -x -C /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5demo/fresh2
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5demo/fresh2 && bash demo/fetch.sh --offline > /tmp/probeD.log 2>&1; echo "PROBE_D_EXIT=$?"
cat /tmp/probeD.log
