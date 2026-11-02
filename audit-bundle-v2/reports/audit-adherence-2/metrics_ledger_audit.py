#!/usr/bin/env python3
"""Count metrics JSONL + ledger facts. Read-only. Never touches cft-named paths."""
import json, os, re, sys
from collections import Counter
from datetime import datetime

def load(path):
    rows=[]
    with open(path, encoding="utf-8") as f:
        for i,line in enumerate(f,1):
            line=line.strip()
            if not line: continue
            try: rows.append(json.loads(line))
            except Exception as e: rows.append({"_parse_error":str(e),"_line":i})
    return rows

def main():
    base="muse-softfloat/docs/metrics"
    for name in sorted(os.listdir(base)):
        if not name.endswith(".jsonl"): continue
        rows=load(os.path.join(base,name))
        print(f"\n== {name}: {len(rows)} rows")
        keys=Counter()
        for r in rows: keys.update(r.keys())
        print(" fields:", dict(keys))
        if name=="plants.jsonl":
            print(" grades:", Counter(r.get("grade") for r in rows))
            print(" waves:", Counter(r.get("wave") for r in rows))
            print(" verifiers:", Counter(r.get("verifier") for r in rows))
            print(" checked_by present:", sum(1 for r in rows if r.get("checked_by")))
            print(" distinct key_sha256:", len(set(r.get("key_sha256") for r in rows)))
            for r in rows:
                if r.get("grade")!="caught":
                    print("  NOT-CAUGHT:", {k:r.get(k) for k in ("wave","verifier","work","plant","shape","grade","graded_by")}, "note:", str(r.get("note"))[:160])
        if name=="passes.jsonl":
            print(" roles:", Counter(r.get("role") for r in rows))
            print(" waves:", Counter(r.get("wave") for r in rows))
            print(" verdicts:", Counter(r.get("verdict") for r in rows if r.get("role") in ("verifier","integration")))
            print(" sent_back true:", sum(1 for r in rows if r.get("sent_back")))
            print(" agents:", sorted(set(r.get("agent") for r in rows)))
            for r in rows:
                if r.get("role") in ("verifier","integration"):
                    print(f"  VERDICT {r.get('wave')} {r.get('agent')} work={r.get('work')} pass={r.get('pass')} a={r.get('a')} b={r.get('b')} verdict={r.get('verdict')} sent_back={r.get('sent_back')} {r.get('start')}->{r.get('end')}")
        if name=="briefs.jsonl":
            for r in rows: print("  BRIEFROW:", {k:r.get(k) for k in ("wave","work","author","base","time_box_min","ceiling_lines")})
        if name=="fetches.jsonl":
            for r in rows: print("  FETCH:", json.dumps(r)[:400])
        if name=="corrections.jsonl":
            print(" accepted:", Counter(str(r.get("accepted")) for r in rows))
            print(" waves:", Counter(r.get("wave") for r in rows))
            for r in rows: print("  CORR:", r.get("wave"), r.get("brief"), "by", r.get("by"), "accepted=", r.get("accepted"), str(r.get("text"))[:100])
        if name=="escalations.jsonl":
            print(" test flags:", Counter(str(r.get("test")) for r in rows), "means:", Counter(r.get("means") for r in rows))
            for r in rows: print("  ESC:", json.dumps(r)[:300])
        if name=="usage.jsonl":
            print(" waves:", Counter(r.get("wave") for r in rows), "sources:", Counter(r.get("source") for r in rows), "models:", Counter(r.get("model") for r in rows))
            print(" agents:", sorted(set(r.get("agent") for r in rows)))
    # brief files vs briefs.jsonl
    print("\n== ledger/briefs files:")
    bf=sorted(os.listdir("ledger/briefs"))
    print(len(bf), bf)
    # ledger files
    print("\n== ledger entry counts (headings ^## YYYY-MM-DD) + Measured/Believed/For line counts:")
    head=re.compile(r"^## (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4}) - (.*)$", re.M)
    for fn in sorted(os.listdir("ledger")):
        if not fn.endswith(".md"): continue
        p=os.path.join("ledger",fn)
        t=open(p,encoding="utf-8",errors="replace").read()
        hs=head.findall(t)
        print(f"  {fn}: entries={len(hs)} Measured:={t.count(chr(10)+'Measured:')+t.startswith('Measured:')} Believed:={t.count('Believed:')} For:={len(re.findall(r'^For:',t,re.M))} READY={t.count('READY')} NOTREADY={t.count('NOT READY')}")
    # lead gaps
    t=open("ledger/lead.md",encoding="utf-8",errors="replace").read()
    stamps=[]
    for m in head.finditer(t):
        try: stamps.append((datetime.strptime(m.group(1),"%Y-%m-%d %H:%M:%S %z"), m.group(2)[:70]))
        except Exception: pass
    print(f"\n== lead.md entries={len(stamps)} span {stamps[0][0] if stamps else None} .. {stamps[-1][0] if stamps else None}")
    for (a,ha),(b,hb) in zip(stamps, stamps[1:]):
        gap=(b-a).total_seconds()/3600
        if gap>2: print(f"  GAP {gap:.1f}h {a} [{ha}] -> {b} [{hb}]")
    # urgent dir listing (names only, skip cft)
    print("\n== ledger/urgent names:", sorted(os.listdir("ledger/urgent")) if os.path.isdir("ledger/urgent") else "ABSENT")
    print("== ledger/board.lock exists:", os.path.exists("ledger/board.lock"))
if __name__=="__main__":
    main()
