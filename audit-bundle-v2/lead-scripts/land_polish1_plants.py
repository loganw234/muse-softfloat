import json

rows = [
    dict(plant=1, shape="current video master specs reverted to the old cut",
         grade="caught",
         note="F1: README 180s/1920x1080 for assembly_v5 vs ffmpeg banner 169.0s 2560x1440"),
    dict(plant=2, shape="site claims every plant ever caught",
         grade="caught",
         note="F2: data.json caught 120 vs build_data rerun 114; by_wave sums to 114"),
    dict(plant=3, shape="broken same-directory link reintroduced",
         grade="caught",
         note="F3: BOARD ../TWIDDLES.md target missing; read as pre-existing vs parent, claim isolated"),
    dict(plant=4, shape="rounding attribute count reverted to four",
         grade="missed",
         note="report clean list reconciled the planted 'all four' via its continuation line against the 5-mode header enum; not isolated"),
    dict(plant=5, shape="clone and Pico LED pins swapped",
         grade="caught",
         note="F4: BOARD GP25/GP16 swap vs msf_led.h + RECORD six-board entry"),
]
key = "26c14c815d39970335de42010a09df19ee0da7eb340dabb88bfb2fe8bee7cbdd"
path = "muse-softfloat/docs/metrics/plants.jsonl"
before = open(path, "rb").read()
assert b"verifier-polish1" not in before
with open(path, "ab") as out:
    if not before.endswith(b"\n"):
        out.write(b"\n")
    for r in rows:
        r.update(wave="polish", verifier="verifier-polish1",
                 work="Post-close stale-information cleanup (polish-stale1)",
                 key_sha256=key, graded_by="lead", checked_by="lead-merge")
        ordered = {k: r[k] for k in ("wave", "verifier", "work", "key_sha256",
                                      "plant", "shape", "grade", "graded_by",
                                      "checked_by", "note")}
        out.write((json.dumps(ordered) + "\n").encode("utf-8"))
after = open(path, "rb").read()
assert after[:len(before)] == before or before.endswith(b"\n")
allrows = [json.loads(x) for x in after.decode("utf-8").splitlines() if x.strip()]
print("plants total=%d caught=%d" % (
    len(allrows), sum(1 for r in allrows if r["grade"] == "caught")))
