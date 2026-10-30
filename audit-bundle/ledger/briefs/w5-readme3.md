**Role:** parcel-w5readme3 (Wave 5 close: README + site refresh)

**Deliverable:** `README.md` and `site/` truthful at
SF-2 close, merge-ready on branch `wave5-readme3`
(worktree `worktrees/w5-readme3`, cut by the lead from
`e9c57fb`). Every number re-derived from the tree, none
copied from this brief.

**State of record to verify yourself (do not trust):**
849 instantiations (Tier 1 783 + Tier 2 66/66);
411,213 committed vectors (+1,117,504 under `standard`);
plants 109/115 at `e9c57fb`; workloads IAS15 six-board
2,001/2,001 + interval + KissFFT 12/12; RECORD.md is
the narrative source. README currently claims 822 /
171,423 (stale).

**Work:**
1. README: full audit pass against the tree - counts,
   implemented families (fifth attribute, rSqrt/hypot,
   exp2/log2 pairs, augmented with its fixed rounding),
   evidence summary (two f32 exhaustives, f16 pairs
   exhaustive), workloads incl. six-board result and
   the LED note, demo/site pointers, TWIDDLES pointer,
   metrics paragraph (refreshed ledgers; plants at a
   named commit). Claim discipline as before: timings
   are records, never performance claims; KissFFT
   never "unmodified"; augmented op-count benefit
   stays a study model, not a shipped claim (interval
   does not consume it yet).
2. Site: rerun the data build (`site/build_data.py`
   idiom), rebuild `site/msf.wasm` + glue with the
   scratch WASM toolchain from the site parcel
   (`scratch/parcel-w5site/` holds the recipe/evidence;
   emsdk lives in scratch - find it, reuse, reinstall
   only into scratch if proven absent), regrow ops/
   vectors samples to the new surface (explog + aug
   pair ops: represent pairs honestly in the UI shape
   the site already has, or exclude them with the
   exclusion printed - never fake a shape), replay
   proof headless (the `site/replay.mjs` shape) over
   the refreshed sample at 0 mismatches, numbers on
   the page stamped "as of" the base commit.
3. `site/README.md` kept in step.

**Fences:** never open/search/list anything with `cft`
in its name; no KissFFT/REBOUND source in repo (demo
pointers only); WASM tooling installs scratch-only;
no visual redesign (numbers/content slots only - the
video/site visual rework is a later owner-gated step).
Owned: `README.md`, `site/**`, `docs/metrics/
briefs.jsonl` (your row). Everything else escalates.
Commits detailed + trailer. Never push/merge. (Pages
deploys from main; your branch merging is what ships
it - the lead verifies the live page after merge.)

**Report:** `scratch/parcel-w5readme3/report.md`
(READY/NOT READY; every changed number with its
derivation command; WASM rebuild + replay counts; aug
representation decision; not-done) + `ledger/
parcel-w5readme3.md`. Script files, Git Bash,
MSF_PYTHON pinned. ~360 min.
