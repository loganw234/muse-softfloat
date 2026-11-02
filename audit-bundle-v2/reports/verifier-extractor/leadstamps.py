import json
from datetime import datetime, timezone

CUT = round(datetime.fromisoformat("2026-10-26T11:31:34-07:00").timestamp() * 1_000_000)
print("CUT micros:", CUT)
P = "C:/Users/logan/.local/share/muse/sessions/2026/10/26/01a17907-4147-7333-a565-56071da9d971/session.jsonl"
stamps = []
for line in open(P, encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    ts = json.loads(line).get("recorded_at")
    if isinstance(ts, int):
        stamps.append(ts)
inc = [t for t in stamps if t <= CUT]
print("total stamped:", len(stamps), "included:", len(inc))
print("max included:", max(inc), datetime.fromtimestamp(max(inc) / 1e6, tz=timezone.utc).astimezone().isoformat(timespec="seconds"))
print("min included:", min(inc), datetime.fromtimestamp(min(inc) / 1e6, tz=timezone.utc).astimezone().isoformat(timespec="seconds"))
above = sorted(t for t in stamps if t > CUT)[:3]
print("first above CUT:", above)
