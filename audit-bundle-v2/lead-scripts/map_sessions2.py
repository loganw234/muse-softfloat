import json, pathlib
base = pathlib.Path.home() / ".local/share/muse/sessions/2026/10/26"
needles = ["verifier-sf0", "rechecker2-sf0", "rechecker-sf0", "approval-audit",
           "verifier-approval", "sf0-evidence", "verifier-extractor"]
for d in sorted(base.iterdir()):
    p = d / "session.jsonl"
    if not p.is_file():
        continue
    text = p.read_text(encoding="utf-8", errors="replace")
    hits = [n for n in needles if n in text]
    first_ts = ""
    for line in text.splitlines()[:50]:
        try:
            rec = json.loads(line)
        except Exception:
            continue
        ts = rec.get("recorded_at") or rec.get("timestamp") or ""
        if ts:
            first_ts = str(ts); break
    print(d.name[:8], first_ts, hits)
