import glob
import json
from datetime import datetime, timezone

CUT = round(datetime.fromisoformat("2026-10-26T11:31:34-07:00").timestamp() * 1_000_000)
BASE = "C:/Users/logan/.local/share/muse/sessions/2026/10/26/01a17907-4147-7333-a565-56071da9d971"

intern = []
for f in glob.glob(BASE + "/subagent/*/session.jsonl"):
    heads = []
    for line in open(f, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        ev = (r.get("payload") or {}).get("event") or {}
        if ev.get("kind") == "started" and isinstance(ev.get("prompt"), str):
            heads.append(ev["prompt"])
    if "reminder observer" in "\n".join(heads[:2]).lower():
        intern.append(f.split("/")[-2])
print("internal-by-phrase count:", len(intern))

mx = 0
for line in open(BASE + "/subagent/88409159-cd18-761d-8c98-951f19425085/session.jsonl", encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    r = json.loads(line)
    ts = r.get("recorded_at")
    if isinstance(ts, int):
        mx = max(mx, ts)
print("probe end:", datetime.fromtimestamp(mx / 1e6, tz=timezone.utc).astimezone().isoformat(timespec="seconds"),
      "cutoff delta s:", (CUT - mx) / 1e6)

n = 0
for f in glob.glob(BASE + "/session.jsonl") + glob.glob(BASE + "/subagent/*/session.jsonl"):
    for line in open(f, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        ts = r.get("recorded_at")
        if isinstance(ts, int) and mx < ts <= CUT:
            n += 1
print("records in (probe_end, cutoff]:", n)
