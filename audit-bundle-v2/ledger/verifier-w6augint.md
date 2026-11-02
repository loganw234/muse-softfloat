# Verifier w6augint ledger note: NOT READY

Copy `worktrees/verify6-augint` (`2221ace`, base oracle parent `50aac59`).
Full note: `scratch/verifier-w6augint/report.md`.

- F1 `board/interval_workload.c:322-323,338`: `aug_prod` assigns tail to both
  outputs and the call site swaps args, so every expansion term list is
  `{tail,tail}` with heads lost. Measured 426/710 rows flip `s3 MISS->HIT`;
  independent Fraction oracle: copy decided-wrong 426, base 0.
- F2 `board/interval_workload.c:420-424`: guard mask omits INEXACT, against
  the design entry and the `.c` comment; inert under the ratified flag table
  (`src/msf_aug.c:286,328,353`), no measured misclassification from it.
- F3 `board/interval_workload.h:74-76`: "exact tiny residual trips the guard"
  contradicts the P1=R2 design (no flag) and the code (quiet).
- F4 `board/interval_run.sh:29-34`: host-build line lacks `src/msf_aug.c`;
  exact-spelled build exits 1 (undefined `msf64_augmented_add/mul`).
  `2221ace` message claims both lists fixed; only the demo list was.
  Demo-spelled build exits 0; ARM compile-only of workload+aug exits 0.
- F5 parcel close-entry records do not reproduce: measured new IW1
  `37b63842...7ba7e4` (not `ae04caf0...`), s3ops `283314->49553`
  (not 63305), total `616754->382993` (not 396745). Base record reproduces.

Probes 1-6 all ran (differential 710 rows; Fraction oracle 693 sphere rows;
guard/primitive readings; exact-spelled builds + ARM `-c`; ops recount).
Not done: per-term dump (oracle used instead), `tools/run.sh standard`,
board run (forbidden), non-finite mini-catalogue, per-bit guard trip id.
