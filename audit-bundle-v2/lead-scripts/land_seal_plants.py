import json
from collections import Counter

SETS = [
    ("verifier-w6captions", "Wave 6 seal: captions + stills for the final cut",
     "339c61fca3d49459655fae3b1aaf9f3970db96fe0cfdc2e0b5b086c471377d97", [
        dict(plant=1, grade="caught",
             shape="tempo scale inverted; regenerated cues drift and overrun the film",
             note="F1: SCALE=124/120 vs assemble.py 120/124; build_cues aborts (191.17 vs 179.03), committed cues match 120/124 so artifacts are not generator output"),
        dict(plant=2, grade="caught",
             shape="caption text differs from the on-screen message",
             note="F5 (+F4): SRT cue1 'I have an idea' vs frame and INTRO_MSG 'I've got an idea'; VTT right, srt!=vtt"),
        dict(plant=3, grade="caught",
             shape="INDEX still time disagrees with filename and recomputation",
             note="F6 (note): INDEX row25 scaled 162.42 vs filename + audit-table recompute 152.42"),
        dict(plant=4, grade="caught",
             shape="VTT timestamps use SRT commas",
             note="F3: VTT cue1 comma timestamps 00:00:01,452 invalid WebVTT (own strict parser)"),
        dict(plant=5, grade="caught",
             shape="one cue overruns into the following beats",
             note="F2: SRT cue2 7258-8742 overlaps cue3 start 7742; midpoint frame already shows cue3's line"),
     ]),
    ("verifier-w6metrics", "Wave 6 seal: final metrics refresh",
     "beff2b211d7a16f3afb7c0d98b0b36598e70a1a5785c185b77ebf1ba4e09e01b", [
        dict(plant=1, grade="caught",
             shape="frozen wave0 usage row edited; append-only prefix broken",
             note="B1: byte-prefix cmp fails, frozen lead out 116106->1161060; parent corroborated by recomputed frozen billed 1,196,128,770 and RECORD wave0 table"),
        dict(plant=2, grade="caught",
             shape="appended usage row inflated; totals no longer reconcile",
             note="B2: verifier-w6popups out 336920 vs independent extractor recount 33692; tip billed gap = B1+B2 to the token"),
        dict(plant=3, grade="caught",
             shape="passes row cites a commit that does not exist",
             note="B3: fixer-w6popups commit ...b053 nonexistent; actual wave6-popups tip ...b052; other 11 author/fixer commits ancestors of base"),
        dict(plant=4, grade="caught",
             shape="briefs row base disagrees with its brief",
             note="N1 (note): own-row base f01dc96 (real ancestor) vs brief-named cdc40ae; other 4 appended briefs rows match their briefs exactly"),
        dict(plant=5, grade="missed",
             shape="wave6 verifier pass mislabelled wave5; per-wave tables break",
             note="not found: coverage counted appended agents by expected list (5+11+19) without checking per-row wave fields; verifier-w6filmretime pass reads wave5 in the copy"),
     ]),
]

path = "muse-softfloat/docs/metrics/plants.jsonl"
before = open(path, "rb").read()
for verifier, _w, _k, _r in SETS:
    assert verifier.encode() not in before, verifier
with open(path, "ab") as out:
    if not before.endswith(b"\n"):
        out.write(b"\n")
    for verifier, work, key, rows in SETS:
        for r in rows:
            r.update(wave="wave6", verifier=verifier, work=work,
                     key_sha256=key, graded_by="lead", checked_by="lead-merge")
            ordered = {k: r[k] for k in ("wave", "verifier", "work", "key_sha256",
                                          "plant", "shape", "grade", "graded_by",
                                          "checked_by", "note")}
            out.write((json.dumps(ordered) + "\n").encode("utf-8"))
after = open(path, "rb").read()
assert after[:len(before)] == before
allrows = [json.loads(x) for x in after.decode("utf-8").splitlines() if x.strip()]
print("plants total=%d caught=%d" % (
    len(allrows), sum(1 for r in allrows if r["grade"] == "caught")))
w6 = [r for r in allrows if r["wave"] == "wave6"]
print("wave6 total=%d caught=%d verifiers=%s" % (
    len(w6), sum(1 for r in w6 if r["grade"] == "caught"),
    sorted(Counter(r["verifier"] for r in w6).items())))
