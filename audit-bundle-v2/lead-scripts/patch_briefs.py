# Add ceiling_text to the two parcel brief rows (committed in 52a6715
# but unpushed; pre-push in-place restatement). The briefs cap
# hand-written lines; round_metrics counts all changed lines incl.
# generated vectors, so its "times ceiling" column needs this text.
import json
import pathlib

P = pathlib.Path("muse-softfloat/docs/metrics/briefs.jsonl")
out = []
for l in P.read_text().splitlines():
    if not l.strip():
        continue
    r = json.loads(l)
    if r.get("author") in ("parcel-f32", "parcel-f64") and "ceiling_text" not in r:
        r["ceiling_text"] = "3,000 hand-written lines (src + test code), generated vectors excluded (brief w1-f%s.md:29)" % r["author"].split("-")[1]
        l = json.dumps(r)
    out.append(l)
P.write_text("\n".join(out) + "\n")
print("patched briefs")
