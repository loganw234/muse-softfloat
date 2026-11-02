#!/bin/bash
# Probe 2b/3: shape-key comparison + totals recomputation.
set -u
DUP="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/dup"
OUT="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/out"
export MSF_PYTHON="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
cd "$DUP"
"$MSF_PYTHON" - <<'EOF'
import json
OUT=r"C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/out"
def load(n):
    return [json.loads(l) for l in open(f"{OUT}/{n}.jsonl")]
for name in ("usage","passes","briefs"):
    f=load(f"frozen-{name}"); a=load(f"app-{name}")
    fk={tuple(sorted(r.keys())) for r in f}; ak={tuple(sorted(r.keys())) for r in a}
    print(f"== {name}: frozen keyshapes={len(fk)} appended keyshapes={len(ak)} match={fk==ak}")
    if fk!=ak:
        print("  frozen:",fk); print("  appended:",ak)
    # parse check
    print(f"  appended rows parse: {len(a)} ok")
    # dup agent rows within appended span (exact-row dup)
    seen={}; dups=0
    for r in a:
        k=json.dumps(r,sort_keys=True)
        seen[k]=seen.get(k,0)+1
        if seen[k]==2: dups+=1; print("  EXACT DUP ROW:",k[:200])
    print(f"  exact-dup rows: {dups}")
    agents=[r.get("agent") for r in a]
    from collections import Counter
    print(f"  agent repeats: {[k for k,v in Counter(agents).items() if v>1]}")
EOF
echo "=== TOTALS ==="
"$MSF_PYTHON" - <<'EOF'
import json
OUT=r"C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/out"
DUP=r"C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/dup"
def loadrows(p): return [json.loads(l) for l in open(p)]
fr=loadrows(f"{OUT}/frozen-usage.jsonl"); tip=loadrows(f"{DUP}/docs/metrics/usage.jsonl")
app=loadrows(f"{OUT}/app-usage.jsonl")
def sums(rows):
    return (sum(r["input_tokens"] for r in rows), sum(r["output_tokens"] for r in rows),
            sum(r.get("cached_tokens",0) for r in rows), sum(r.get("messages",0) for r in rows))
fi,fo,fc,fm=sums(fr); ai,ao,ac,am=sums(app); ti,to,tc,tm=sums(tip)
print(f"frozen:    in={fi:,} out={fo:,} billed={fi+fo:,} cached={fc:,} msgs={fm}")
print(f"appended:  in={ai:,} out={ao:,} billed={ai+ao:,} cached={ac:,} msgs={am}")
print(f"tip total: in={ti:,} out={to:,} billed={ti+to:,} cached={tc:,} msgs={tm}")
print(f"frozen+appended: in={fi+ai:,} out={fo+ao:,} billed={fi+ai+fo+ao:,}")
print("ledger claims: frozen billed=1,196,128,770 appended billed=+221,936,428 (in 220,313,353/out 1,623,075/msgs 2,344) refreshed billed=1,418,065,198 (in 1,410,803,658/out 7,261,540/cached 1,379,156,504/msgs 10,100)")
EOF
