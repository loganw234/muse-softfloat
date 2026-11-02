#!/bin/bash
# Probe 3e: recompute wave0 per-agent table from PARENT bytes, compare with RECORD.md.
set -u
export MSF_PYTHON="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
export OUT="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/out"
"$MSF_PYTHON" - <<'EOF'
import json, re
OUT=r"C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/out"
DUP=r"C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/dup"
par=[json.loads(l) for l in open(f"{OUT}/parent-usage.jsonl", encoding="utf-8")]
pp=[json.loads(l) for l in open(f"{OUT}/parent-passes.jsonl", encoding="utf-8")]
w0=[r for r in par if r["wave"]=="wave0"]
print(f"parent wave0 usage rows: {len(w0)}")
tools={r["agent"]: r["tool_uses"] for r in pp}
rec={}
for line in open(f"{DUP}/docs/RECORD.md", encoding="utf-8"):
    m=re.match(r"\| ([^|]+) \| ([^|]+) \| (\d+) \| ([^|]+) \| (\d+) \| ([\d,]+) \| ([\d,]+) \| ([\d,]+) \|", line)
    if m:
        agent,model,passes,mins,tu,outt,intt,cached=m.groups()
        rec[(agent.strip(),model.strip())]=(int(outt.replace(",","")),int(intt.replace(",","")),int(tu))
print(f"RECORD wave0 table rows: {len(rec)}")
bad=0
for r in w0:
    k=(r["agent"],r["model"])
    if k not in rec:
        print("NOT IN RECORD:",k); bad+=1; continue
    o,i,t=rec[k]
    if (o,i,t)!=(r["output_tokens"],r["input_tokens"],tools.get(r["agent"])):
        print("DIFF",k,"committed-parent=",(r["output_tokens"],r["input_tokens"],tools.get(r["agent"])),"record=",(o,i,t)); bad+=1
print("wave0 parent-vs-RECORD diffs:",bad)
tip=[json.loads(l) for l in open(f"{DUP}/docs/metrics/usage.jsonl", encoding="utf-8")]
lead=[r for r in tip if r["agent"]=="lead" and r["wave"]=="wave0"][0]
print("tip lead wave0 out:",lead["output_tokens"],"vs RECORD 116106")
EOF
