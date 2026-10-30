import json, pathlib, collections

sess = pathlib.Path(r"C:\Users\logan\.local\share\muse\sessions\2026\10\26\01a17907-4147-7333-a565-56071da9d971")
files = [("lead", sess/"session.jsonl")] + [(p.parent.name, p) for p in sorted((sess/"subagent").glob("*/session.jsonl"))]

seen = {}
per = []
for label, p in files:
    models = collections.Counter(); calls=set(); objs=0; mc=0
    first=None; last=None; texts=[]
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        try: o=json.loads(line)
        except Exception: continue
        ts=o.get("recorded_at")
        if isinstance(ts,int):
            first=ts if first is None else min(first,ts); last=ts if last is None else max(last,ts)
        payload=o.get("payload") or {}; ev=payload.get("event") if isinstance(payload,dict) else None
        if isinstance(ev,dict):
            if ev.get("kind")=="model_completed":
                mc+=1; u=ev.get("usage") or {}; key=(ts, ev.get("model"), u.get("input_tokens"),u.get("output_tokens"),u.get("cached_tokens"),u.get("cache_read_tokens"),u.get("cache_write_tokens"),u.get("reasoning_tokens"),ev.get("duration_ms"))
                models[str(ev.get("model"))]+=1
                seen.setdefault(key,[]).append(label)
            elif ev.get("kind")=="assistant_tool_calls_committed":
                for c in ev.get("tool_calls") or []:
                    calls.add(c.get("call_id") or c.get("id"))
            elif ev.get("kind")=="started" and isinstance(ev.get("prompt"),str):
                texts.append(ev["prompt"][:90].replace("\n"," "))
    dur = 0 if first is None else (last-first)/1e6
    per.append((label, mc, len(calls), round(dur,1), dict(models), texts[:1]))

dups = {k:v for k,v in seen.items() if len(v)>1}
cross = {k:v for k,v in dups.items() if len(set(v))>1}
print("files",len(files),"model_completed total raw",sum(x[1] for x in per),"unique keys",len(seen),"dup keys",len(dups),"cross-file dup keys",len(cross))
for row in per:
    print(row)
