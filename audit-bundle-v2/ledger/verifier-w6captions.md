# verifier-w6captions — captions + stills verification

**Verdict: NOT READY** (5 blockers, 3 notes). Full evidence:
`scratch/verifier-w6captions/report.md` (+ own scripts in
`scratch/verifier-w6captions/scripts/`).

Copy `worktrees/verify6-captions` (detached `c537e0d`, parent
`cdc40ae`) read-only; all runs in a duplicate under Git Bash with
`MSF_PYTHON` pinned to the workspace `.venv`. Assembly probed at
179.030 s. 77 cues/file (intro 1 / idea 25 / why 32 / gitvisual 11 /
outro 8); 15 midpoint frames viewed; all 30 stills viewed;
`tools/run.sh standard` PASS in the duplicate; diff vs parent limited
to the owned files.

- **F1 (blocker):** `video/captions.py` cannot regenerate the
  artifacts — `SCALE = 124/120` is inverted vs `assemble.py`'s
  `120/124`; `build_cues()` aborts (`191.17` vs `179.03`), zero bytes
  written. Committed cue times match 120/124, so they are not
  generator output.
- **F2 (blocker):** SRT cue 2 (ends 08.742) overlaps cue 3 (starts
  07.742); at cue 2's midpoint the frame already shows cue 3's line.
- **F3 (blocker):** VTT cue 1 uses comma timestamps — invalid WebVTT.
- **F4 (blocker):** srt and vtt disagree (cue 1 text, cue 2 end).
- **F5 (blocker):** SRT cue 1 `Hey Muse, I have an idea...`
  contradicts the frame (`I've got`) and `INTRO_MSG`; VTT is right.
- **F6 (note):** `stills_v6/INDEX.md` row 25 Scaled `162.42` should be
  `152.42` (filename + recompute agree).
- **F7 (note):** still-01 filename time (2.90) is coarser than the
  exact grab instant (2.903); exact-time grabs are byte-identical —
  stills are stable.
- **F8 (note):** committed hashes/sizes (srt 5321 bytes `0e285a72…`,
  vtt `24bc4e71…`) match neither the claimed `490568F2…/AA53BC4D…`
  hashes nor the claimed 5323-byte SRT size.
