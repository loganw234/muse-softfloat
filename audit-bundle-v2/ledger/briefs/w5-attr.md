**Role:** parcel-w5attr (SF-2 Step 1: fifth rounding attribute)

**Deliverable:** `roundTiesToAway` as the fifth public
rounding attribute across all 255 attribute-carrying rows,
zero new inventory rows, merge-ready on branch
`wave5-attr` (worktree `worktrees/w5-attr`, base `889ec2e`).
Time box: 600 min wall; at 480 min file a what-is-left note
and continue only what fits.

**Governing:** `docs/studies/SF-2.md` Secs. 2, 6-9 and the
attribute study (`scratch/sf2-attribute/report.md`, read in
full). In any conflict the study's executed evidence wins
over SF-2's summary; the study's stop conditions bind.

**Work, in this order:**
1. Kernel: the two `src/msf_string.c` cases the study names
   (`dec_round_inc`, `to_hex_generic` precision switch).
   Nothing else in `src/` should need a change; if generation
   exposes a third out-of-pack rounding site, STOP per study
   stop condition (1) and report.
2. Seam: `tools/gen_tables.py` header prelude gains
   `MSF_ROUND_TIES_TO_AWAY = 4` (rewrite the named-forms-only
   sentence); regenerate header/coverage (contents otherwise
   unchanged); `tests/VECTORS.md` token note; a new runner
   negative control swapping te/ta (must be refused).
3. Generators: mode lists to five modes per the study's file
   list incl. the ta-arm reference fixes (`gen_vectors_xf.py`
   2 arms, `gen_vectors_str.py` 3 arms, `gen_vectors_f64.py`
   pool modulo). Regenerate committed sets; `ta` at
   **directed-mode volume** (the tz column, ~+20k lines) with
   the study's tie-rich directed design - random sets are
   tie-poor and are not the gate.
4. Trig/sqrt relabel: te sets replayed relabeled `ta` with
   provenance noting the relabel; the no-exact-ties argument
   (Niven for sinPi/cosPi, the midpoint-square argument for
   sqrt) written into the parcel report and second-read there
   (study stop condition 2 if it fails). Never present
   relabeled lines as independently decided.
5. Gates (script files, Git Bash, MSF_PYTHON pinned):
   Berkeley `-rnear_maxMag` level-1 replay for every covered
   function; binary16 five-mode exhaustive streams per the
   study; `smoke` + `standard` PASS; negative controls
   watched to fail incl. (a) ta routed to toward-zero in one
   string case (scratch build), (b) te/ta wrong-mode control,
   (c) one flipped relabeled trig expectation. Raw MPFR
   `RNDNA` is prohibited (study Sec. 2.2); the
   `mpfr_round_nearest_away` macro only inside its fences,
   and only if a generator actually needs it. Determinism:
   regenerated committed files byte-stable across two runs;
   no wall-time fields in committed files.

**Owned files:** `src/msf_string.c`, `tools/gen_tables.py`,
generated `include/muse_softfloat.h` + `docs/COVERAGE.tsv`,
`tests/{gen_vectors*,VECTORS.md}`, `tests/vectors/*.vec`
(attr sets), `tools/run.sh` (control only),
`docs/metrics/briefs.jsonl` (your row). Escalate - do not
touch - anything else; in particular no `src/msf_roundpack.c`,
no tables/operations rows, no BOARD/RECORD/README wording
beyond listing what the lead must restate at merge.

**Report:** `scratch/parcel-w5attr/report.md` (first line
READY/NOT READY; per-family ta evidence table with counts;
relabeled-vs-decided volumes split; the theorem notes; not-
done list) + `ledger/parcel-w5attr.md` (design entry BEFORE
code, results entry after). Commit on the branch with a
detailed body ending `Co-Authored-By: Muse Code
(muse-wonder-full-1.0) <noreply@meta.ai>`. Never push or
merge. No board flashing (lead replays after merge). Clean
room: nothing with `cft` in its name; Berkeley stays an
executed oracle. Structured complete/evidence/unresolved.
