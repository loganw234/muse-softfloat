# Patch the just-folded Wave 1 pass rows: the extractor labelled the
# parcels/regaters/verifiers "surveyor" (its role_for() does not know
# these names, and the Spark verifiers arrived as session UUIDs), so no
# commit/verdict fields attached. Roles and reported tips are facts from
# the ledgers: parcels reported checkpoints 6c1bc01/5153324, regaters
# reported READY tips 26c76aa/cb10ee2, verifiers' (a)/(b) counts are as
# their reports count them (f32: (a)1 (b)4; f64: (a)3 (b)3), both NOT
# READY / sent back on the planted copies. Rows are uncommitted, so this
# is a pre-push in-place restatement.
import json
import pathlib

P = pathlib.Path("muse-softfloat/docs/metrics/passes.jsonl")
PATCH = {
    "parcel-f32": {"role": "author", "commit": "6c1bc010b80a17629b180cd0280a20aedbd48960"},
    "parcel-f64": {"role": "author", "commit": "51533243a29e3a026493b8e3e04d2b2711ac4b4a"},
    "regater-f32": {"role": "fixer", "commit": "26c76aafae1daad27fade6e19df2764d96980dc8"},
    "regater-f64": {"role": "fixer", "commit": "cb10ee298a25d92c4ab3da26d4d2f2d7a74f702a"},
    "verifier-w1f32": {"role": "verifier", "a": 1, "b": 4, "verdict": "NOT READY", "sent_back": True},
    "verifier-w1f64": {"role": "verifier", "a": 3, "b": 3, "verdict": "NOT READY", "sent_back": True},
}
lines = P.read_text().splitlines()
out = []
for l in lines:
    if not l.strip():
        continue
    r = json.loads(l)
    if r.get("wave") == "wave1" and r.get("agent") in PATCH:
        r.update(PATCH[r["agent"]])
        r["note"] = (r.get("note", "") + "; role/commit/verdict restated by lead fold from ledgers (extractor role_for gap)").strip("; ")
        l = json.dumps(r, separators=(",", ":"))
    out.append(l)
P.write_text("\n".join(out) + "\n")
print("patched")
