"""Append Agent A text/pacing entries to the two study ledgers."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

intro_entry = """

## v3 text/pacing pass (study-video-textpacing, Agent A)

Delivered beside v1/v2 in `scratch/study-video-intro/` (priors
byte-identical; repo untouched; nothing committed). Full evidence:
`textrev-report.md` (first line READY; copy table; dwell audit 0
violations under the stated persistence convention, solo-reading
risk named); scripts `render_v3.py` (+ idea/why siblings below),
`audit_textrev.py`/`audit3.json`, `verify3.py`/`verify3.json`,
`measurements3.json`.

- `intro3.mp4` - 7.0 s, NATIVE 2560x1440 (v2 master was 1080p),
  210/210 decoded rc 0. Whole design scaled parametrically (K=4/3);
  period centroid RE-MEASURED at 1440p: raster (1561.46, 361.5),
  metrics agrees within 0.5 px; mid-dive proof error 0.6 px
  (`still3_period_proof.png`, eyeballed); intro clamp 0.0 px.
  Message holds 1.5-4.5 s (rule dwell 3.0 s for 6 words), same
  2.0 s dive, white hold re-verified 0 non-white px.
- `outro3.mp4` - 8.5 s, 2560x1440, 255/255 rc 0. First frame
  decoded (2,3,8) dominant (source 3,4,9, spec unchanged). Dots
  centroid re-measured (1320.0, 545.3); outro clamp 0.146 px.
  Reply bubble cut to "Identical on all 6 boards." (849/411,213
  stay on the stat cards); left panel definitions block collapsed
  to one tag (full definitions quoted in the report); panels now
  reveal in 6 staged beats, <=2 new lines each.
- Frames stream (v2 buffered all frames; at 1440p that breaks the
  memory ceiling). Words intro+outro 97 -> 52 (-46%).
- Assembly: intro+outro now 15.5 s (was 11.0 s); handoff VALUES
  unchanged (white / near-black); owner copy sign-off still open.
"""

why_entry = """

## v3 text/pacing pass (study-video-textpacing, Agent A)

Status: READY (both segments). Brief:
ledger/briefs/study-video-textpacing.md (dwell from word count:
smallest 0.5 s multiple >= max(1.5, 0.5 + words/2.5); headlines
<=6 w; body <=10 w; <=2 new lines/beat; plain language; ~1/3
word cut). Same a73e97d facts / SF-0 discipline; priors
byte-identical; repo untouched; nothing committed. Report:
scratch/study-video-intro/textrev-report.md (READY; copy table;
dwell audit 0 violations on the persistence convention stated
there, with the stricter solo-dwell reading named: 59/73 blocks
under on solo intervals - lead/owner call).

- Segment A': scratch/study-video-idea/idea2-1440p.mp4, 22.5 s
  (was 14.5), 675/675 frames rc 0, 881,976 B. Script
  render_idea2.py; stills-idea2/. Words 195 -> 132 (-32%).
  Jargon plain per brief ("the next number the chip can hold",
  number-line prompt line cut). White 0.2/22.3 s exact.
- Segment B': scratch/study-video-why/why3-1440p.mp4, 33.5 s
  (was 32.0), 1005/1005 rc 0, 1,574,914 B. Script render_why3.py;
  stills3/. Words 337 -> 198 (-41%). Lineup recap scene CUT
  (zero unique claims; its dwell could not fit the 160 s film);
  bootrom asterisk + two "e.g." lines cut as redundant (named
  in the copy table); one source tag per option scene.
  White 0.2/33.3 s exact.
- Budget: front pair (incl. intro3/outro3) 57.5 -> 71.5 s;
  with gitvisual4 88.0 s the film is 159.5 s <= 160 s before
  music (v4 assembly 145.5 s). gitvisual5 (Agent B) duration
  was still in flight at this writing.
"""

p1 = ROOT / "ledger" / "study-video-intro-outro.md"
p2 = ROOT / "ledger" / "study-video-why-v2.md"
t1 = p1.read_text(encoding="utf-8")
assert "v3 text/pacing pass" not in t1
p1.write_text(t1 + intro_entry, encoding="utf-8")
t2 = p2.read_text(encoding="utf-8")
assert "v3 text/pacing pass" not in t2
p2.write_text(t2 + why_entry, encoding="utf-8")
print("appended", p1, p2)
