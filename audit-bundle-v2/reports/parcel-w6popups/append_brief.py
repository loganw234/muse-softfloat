"""Append this parcel's row to docs/metrics/briefs.jsonl (binary append)."""
import json

ROW = {
    "wave": "wave6",
    "work": (
        "Chase popup cards generalised: the seven POPUP5 cards in "
        "video/segments/gitvisual.py now carry general descriptions plus "
        "each system's project total (20 parcels, 3 escalations, "
        "36 verifiers, 150 planted bugs, 411213 smoke + 1117504 standard, "
        "35 studies, 25 merges to main), every count derived by script "
        "from process_graph.json/history.json (frozen at a73e97d) or the "
        "HEAD tree (tools/run.sh budget output / RECORD); per-card "
        "POPUP_WORDS identical to base so POPUP_DWELL/ARRIVALS/T_BRIDGE/"
        "T_REPLAY/SHIFT/GATES/LEGS/TOTAL are unchanged; gitvisual7.mp4 "
        "regenerated (108.0 s, 2560x1440@30, silent) with one still per "
        "new card viewed; cursor on every gate rank at t0; tools/run.sh "
        "standard PASS"
    ),
    "author": "parcel-w6popups",
    "base": "f01dc96055f24b4aa5450bdadabf44fa5308abb9",
    "time_box_min": 240,
    "ceiling_lines": 0,
    "ceiling_text": (
        "no line ceiling stated in brief w6-popups.md; owned-files list "
        "is the bound (video/segments/gitvisual.py POPUP5 strings and "
        "comment only, regenerated gitvisual7.mp4, this row)"
    ),
}

with open("docs/metrics/briefs.jsonl", "ab") as f:
    f.write((json.dumps(ROW) + "\n").encode("utf-8"))
print("appended", ROW["author"])
