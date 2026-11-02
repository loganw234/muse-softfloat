# parcel-polish1 (lead-authored)

- Brief: `ledger/briefs/polish-stale1.md`. Base `400b271`, branch
  `polish-stale1`, worktree `worktrees/polish-stale1`.
- Author tip: `6aa720e80f43db12c089ad33553192a72b7359cd`
  (24 files, comments/docs/regenerated data only).
- Claim: every present-tense stale claim from the 2026-10-29 Spark
  audit is fixed; frozen `audit-bundle/` untouched; historical
  RECORD lines restated by appendix only.
- Evidence: `tools/run.sh standard` PASS on the branch
  (`scratch/lead/gate_polish1_standard.log`): drift check
  byte-identical, 411,213 committed + 1,117,504 standard vectors,
  augmented exhaustive pool 0 mismatches.
- Regenerations: `tools/gen_tables.py` (only the decimal comment
  changed in the header), `site/build_data.py` (plants 114/120).
