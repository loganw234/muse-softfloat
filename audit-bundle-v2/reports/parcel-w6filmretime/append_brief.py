import json
from pathlib import Path
p = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-filmretime\docs\metrics\briefs.jsonl")
row = {
    "wave": "wave6",
    "work": "Film retime to the 3-minute cap: duplicate WHY-NOT title scene deleted from why (idea poses it once), intro/outro phone-camera crops supersampled SS=2 (5120x2880 internal, output stays 2560x1440, period centroid re-measured, proof error 0.2 px, join solids exact), segment text dwell extended to exactly 185.0 s native (intro 7, idea 26, why 32, gitvisual 108, outro 12 = 179.0 s at 124 BPM) with gitvisual gate ranks/legs unchanged and sync re-measured at-event 0.000 px; tools/run.sh standard PASS",
    "author": "parcel-w6filmretime",
    "base": "101b4aa98fc9f53005778fb424197d7ec7d26c82",
    "time_box_min": 480,
    "ceiling_lines": 0,
    "ceiling_text": "no line ceiling stated in brief w6-filmretime.md; owned-files list is the bound (video/segments/{idea,why,render_why,intro_outro,gitvisual}.py, video/assemble.py SEGMENTS only, this row, regenerated segment artifacts)",
}
data = p.read_bytes()
assert b"parcel-w6filmretime" not in data
if not data.endswith(b"\n"):
    data += b"\n"
line = (json.dumps(row, ensure_ascii=False) + "\n").encode("utf-8")
with p.open("ab") as f:
    f.write(line)
# verify: last line parses, earlier bytes untouched size check
after = p.read_bytes()
assert after[:len(data)] == data and len(after) == len(data) + len(line)
assert json.loads(after.splitlines()[-1])["author"] == "parcel-w6filmretime"
print("appended", len(line), "bytes; total lines", len(after.splitlines()))
