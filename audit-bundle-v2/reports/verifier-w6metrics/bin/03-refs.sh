#!/bin/bash
# Probe 2c/3b: parent-byte frozen sums, appended per-agent table, commit ancestry.
set -u
DUP="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/dup"
OUT="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/out"
export MSF_PYTHON="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
cd "$DUP"
"$MSF_PYTHON" - <<'EOF'
import json
OUT=r"C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/out"
par=[json.loads(l) for l in open(f"{OUT}/parent-usage.jsonl")]
fi=sum(r["input_tokens"] for r in par); fo=sum(r["output_tokens"] for r in par)
print(f"PARENT frozen: in={fi:,} out={fo:,} billed={fi+fo:,} (ledger claims 1,196,128,770)")
app=[json.loads(l) for l in open(f"{OUT}/app-usage.jsonl")]
print("=== appended usage per agent (wave agent out in msgs) ===")
for r in app:
    print(f"{r['wave']:>6} {r['agent']:<28} out={r['output_tokens']:>8,} in={r['input_tokens']:>11,} msgs={r['messages']:>4}")
ao=sum(r["output_tokens"] for r in app)
print(f"appended out sum={ao:,} (ledger claims 1,623,075)")
EOF
echo "=== commit existence + ancestry vs cdc40ae ==="
for sha in 3f29682ef1bff6af263ba0f722af8aa65875499c 498a91667984a374c211ad2ef746618a012c570d 5ce5ac5b81472d7f14420c35ba1aca8b5605ef57 eda5812d2803b113fe0eaa37b626d5d097a4a979 5b53bf3db94100b401eb6f7bef516472d9d28dc1 b6e08fd2a1fa555c561c33b0c20c2fca5b3d970b 1bc097977e44f86be4d3c984bbaf19ca8225fd63 77e6e647cac519a35975b1adadecfb157e0c93b5 245a4f5b0aa7108f99852b385b51c397d44b6ae2 1cfed360d2a456199810a605bcdb078fa731af19 0708e2e1a91dd9c1f9a30bf7d7c3fea8ef51ee78 ef0215b140a0eeb12ea3d4e64113a4ea0421b053; do
  short=${sha:0:7}
  if git cat-file -e "$sha" 2>/dev/null; then
    if git merge-base --is-ancestor "$sha" cdc40ae 2>/dev/null; then anc="ancestor-of-base"; else anc="NOT-ancestor-of-base"; fi
    echo "$short exists $anc"
  else
    echo "$short MISSING"
  fi
done
echo "=== briefs bases ==="
"$MSF_PYTHON" -c "
import json
for l in open('$OUT/app-briefs.jsonl'):
    r=json.loads(l); print(r.get('author'), r.get('base'), r.get('wave'))
"
