import glob
import json
from datetime import datetime, timezone

CUT = round(datetime.fromisoformat("2026-10-26T11:31:34-07:00").timestamp() * 1_000_000)
BASE = "C:/Users/logan/.local/share/muse/sessions/2026/10/26/01a17907-4147-7333-a565-56071da9d971"
PROBE_END = round(datetime.fromisoformat("2026-10-26T11:31:29-07:00").timestamp() * 1_000_000)

hits = []
for f in glob.glob(BASE + "/session.jsonl") + glob.glob(BASE + "/subagent/*/session.jsonl"):
    for line in open(f, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        ts = r.get("recorded_at")
        if isinstance(ts, int) and PROBE_END < ts <= CUT:
            ev = (r.get("payload") or {}).get("event") or {}
            hits.append((f.split("/")[-2][:8], ts, ev.get("kind"), ev.get("model")))
print("records in (11:31:29, cutoff]:", len(hits))
for h in hits[:20]:
    print(h)
