import json

rows = [
    dict(plant=1, shape="judge map gives the old cut's specs for the current film",
         note="F1: claimed 180s 1920x1080; probed assembly_v5 169.000s 2560x1440 no audio (180s/1080p is final.mp4)"),
    dict(plant=2, shape="map claims every plant ever caught",
         note="F2: claimed 145/145; mechanical totals rows=145 caught=138; Status figure correct"),
    dict(plant=3, shape="judge reproduction step demands the physical board",
         note="Boundaries: literal step-4 command is run_demo.sh board, step names no board prerequisite, boardless judge cannot perform it as written (isolated unnumbered)"),
    dict(plant=4, shape="map quotes the pre-augint interval hash as current",
         note="F3: map ce81d66e...a9aec vs runner ae04caf0...c1422 rows=710 in verifier's own demo run"),
    dict(plant=5, shape="demo interval expectation off by one hex digit",
         note="F4: expected file ends ..66c1423 vs program/BOARD/RECORD ..66c1422; interval leg cannot pass"),
]
key = "4dcf5c2af438bbdb36a859747d2038a351dc27d2449838c288877efa9e4ba6bd"
path = "muse-softfloat/docs/metrics/plants.jsonl"
before = open(path, "rb").read()
assert b"verifier-w6judgemap" not in before
with open(path, "ab") as out:
    if not before.endswith(b"\n"):
        out.write(b"\n")
    for r in rows:
        r.update(wave="wave6", verifier="verifier-w6judgemap",
                 work="Wave 6 item 5: judge's map (README start-here)",
                 key_sha256=key, grade="caught", graded_by="lead",
                 checked_by="lead-merge")
        ordered = {k: r[k] for k in ("wave", "verifier", "work", "key_sha256",
                                      "plant", "shape", "grade", "graded_by",
                                      "checked_by", "note")}
        out.write((json.dumps(ordered) + "\n").encode("utf-8"))
after = open(path, "rb").read()
assert after[:len(before)] == before
allrows = [json.loads(x) for x in after.decode("utf-8").splitlines() if x.strip()]
print("plants total=%d caught=%d" % (
    len(allrows), sum(1 for r in allrows if r["grade"] == "caught")))
