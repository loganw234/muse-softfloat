# parcel-w6popups — chase popup cards generalised + project totals

Branch `wave6-popups` on base `f01dc96`; brief
`ledger/briefs/w6-popups.md`; full evidence in
`scratch/parcel-w6popups/report.md`.

- The seven chase popup cards in `video/segments/gitvisual.py`
  (`POPUP5`) now read as general descriptions with each system's
  project total: PARCELS "work is divided / 19 parcels total",
  ESCALATIONS "questions go to lead / 20 filed, 3 fixes",
  VERIFIERS "recheck every parcel independently / 36 verifiers total",
  PLANTS "traps test the checkers / 150 planted bugs",
  GATES "nothing merges unless all green /
  411,213 smoke + 1,117,504 standard",
  STUDIES "scout the ground before building / 35 studies total",
  MAIN "finished work joins here / 25 merges to main".
  Every count derived by script (frozen `process_graph.json` /
  `history.json` at a73e97d, or the HEAD tree for gates);
  frozen-vs-HEAD deltas (plants 150 vs 155, parcels 19 lanes + spine,
  escalations 3 fixer lanes vs 20 filings) listed with reasons.
  Fixer send-back: PARCELS card now counts the 19 drawn parcel lanes
  (the 20th "author" pass is the lead's wave0 spine, not a parcel);
  ESCALATIONS card now carries both numbers (20 filings in
  `docs/metrics/escalations.jsonl` waves 1-5, 3 fixer lanes drawn).
  Per-card `POPUP_WORDS` still `[7,9,8,8,11,9,9]`; mp4 regenerated
  (108.0 s, silent); parcel briefs row restated in place; standard
  not re-run (copy-strings-only diff vs the passing run).
- Per-card `POPUP_WORDS` identical to base (`[7,9,8,8,11,9,9]`);
  `POPUP_DWELL`, `ARRIVALS`, `T_BRIDGE` 46.0, `T_REPLAY` 48.5,
  `SHIFT` 17.5, `GATES` ranks/t0/t1, `LEGS`, `TOTAL` 108.0 all
  identical (before/after import dumps; only the copy section differs).
- `gitvisual7.mp4` regenerated (193 s render): probed 108.0 s,
  2560x1440@30, silent, 3240 decoded frames; one still per new card
  viewed (text inside card, no overflow, legible at 1440p).
- Cursor exactly on every gate rank at t0 (44/69/140), monotonic;
  `tools/run.sh standard` PASS in 74 s (smoke total 411,213,
  standard extras total 1,117,504 — corroborating the GATES card).
- Diff vs base limited to the three owned files; no assembly
  (lead assembles at merge).
