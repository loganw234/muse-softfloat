# verifier-w6filmretime — verdict NOT READY

Copy `worktrees/verify6-filmretime` @ `a1e83d9` (parent `101b4aa`).
Full evidence: `scratch/verifier-w6filmretime/report.md` (+ probe scripts
`probe1_durations.py`, `probe3_dwells.py`, `probe5_gitvisual.py`,
`probe24_stills_ss.py`, stills `p2_*`/`p4_*`). Renders and
`tools/run.sh standard` ran in duplicate `tmp/v6dup`; the copy is untouched.
Probed MP4 reality: 7/26/32/108/12 s = 185.0 native, all 2560x1440@30, silent.

Findings:

1. (blocker) Cap claim false as coded. `assemble.py`: `tempo = 120/120`
   (parent: 120/124), why SEGMENTS row stale at 29.0 (actual 32.0);
   duplicate-assembled product probed at 185.00 s > 180 s cap, cuts on the
   unscaled grid; script join checks sample scaled times (6.7/31.8/…), not
   the true cuts; tempo edit exceeds "SEGMENTS only" scope.
2. (blocker) `idea.py` BLOCKS question rows degenerate: gone remapped to
   scene start T_Q=21.5, dwells 0.0 / −0.5 vs parcel "zero violations".
   Renders unaffected (scene runs to FADE_T; true dwells 3.5/3.0 ≥ RULE).
3. (blocker) kissfft gate rank 70.0 = G1_RANK+1.0 ≠ merge rank 69
   (parent: no +1.0); cursor_rank non-monotonic, 70→69 drop at t=79.5.
4. (note) SS=2 verified in shipped pixels (MSE 3.4 vs SS=1 407.0; proof
   error 0.2; clamps 0.0/0.25; join solids white/near-black) but code
   default is `MSF_SS="1"` (2560x1440 internal), so the tree does not
   reproduce its own measurements3.json/MP4s at defaults; `scale_K`
   records base K.
5. (note) Dead `scene_workloads`/workload constants remain in `why.py`
   (pre-existing; title-scene copy fully deleted, question posed once in
   idea's closing scene, why opens white→spec — stills verified).

Passing: all segment durations/res/fps/silence; why+intro+outro dwells;
popup dwells = RULE+0.5; TOTAL 108.0; legs 8/5/7; windows 9/9/8.5; cursor on
gate ranks through windows; IAS/LAST ranks exact; `tools/run.sh standard`
PASS in duplicate (50 s); diff limited to owned files + briefs row +
artifacts; claim discipline (records only, silent).
