# verifier-w6popups — verdict **NOT READY** (`8507695`, parent `f01dc96`)

Full evidence: `scratch/verifier-w6popups/report.md`
(scripts `scratch/verifier-w6popups/scripts/probe*.py`, frames
`scratch/verifier-w6popups/mp4frames/`). Duplicate:
`worktrees/dup-v6popups`. Copy never modified (status clean).

Findings (blocker = wrong answer/regression vs the parcel brief):

1. (blocker) PARCELS code reads "20 parcels total"; drawn lanes are 19
   (spine E001 is the lead's wave0 episode, not a parcel).
   mp4/ledger/row correctly read 19.
2. (blocker) VERIFIERS code reads "35 verifiers total"; 36 verifier
   lanes drawn. mp4/ledger/row correctly read 36.
3. (blocker) PLANTS code reads "155 planted bugs"; frozen graph
   accounting is 150 (155 is the HEAD `plants.jsonl` mechanical total:
   148 caught + 7 missed). Parcel discipline requires the
   frozen-graph-consistent 150. mp4/ledger/row correctly read 150.
4. (blocker) GATES code reads "1,171,504 standard"; generator parts
   (917,504 + 200,000), `RECORD.md` (×4), and the live standard run
   (`total 1117504 passed`) all give **1,117,504**. Transposed digits.
   mp4/ledger/row correctly read 1,117,504. Smoke 411,213 correct.
5. (blocker) STUDIES code line (7 words) makes `POPUP_WORDS`
   `[7,9,8,8,11,11,9]` vs base `[7,9,8,8,11,9,9]`; by import,
   `POPUP_DWELL/ARRIVALS/T_BRIDGE/T_REPLAY/SHIFT/GATES/LEGS/TOTAL`
   ALL differ (TOTAL 108.5 vs sealed 108.0). Timing freeze broken.
   mp4 shows the fitting 5-word line ("scout the ground before
   building").
6. (blocker) Committed mp4 text ≠ committed `POPUP5` on 5 of 7 cards
   (probe-3 exact-match rule fails). The mp4 carries the ledger/row
   numbers and 108.0 s duration — the code is the wrong side, so a
   re-render from this code would also regress the artifact.

Notes (no blockers): ESCALATIONS ("20 filed, 3 fixes": 20 filings
waves 1–5, 3 fixer lanes) and MAIN (25 merges into main) verified
correct; cursor-on-gate-rank + monotonicity hold; `tools/run.sh
standard` PASS in duplicate (60 s; smoke 411,213, extras 1,117,504,
aug pool 5,505,024); diff vs parent limited to the three owned files
with code changes confined to the comment + `POPUP5`; briefs row 39
numbers match all recounts; all seven mp4 stills viewed — text inside
card, legible, titles match legend.

Fix: correct the five code strings to the mp4/ledger strings (STUDIES
line "scout the ground before building"), re-prove the import-equality
dump against `f01dc96`, confirm no re-render is needed (code timeline
returns to 108.0 s = mp4 duration), re-run standard.
