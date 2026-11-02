**Role:** parcel-w6augint (Wave 6 queue item 1: augmented arithmetic earns its place)

**Base:** `50aac59f6035d56c37340ff07c59252cfd22d5d4`, branch
`wave6-augint`, worktree `worktrees/w6-augint`. Work only there.

**Job:** make the interval workload's exact stage actually consume
the Clause 9.5 augmented operations. Today
`iw_sphere_stage3_exact` (board/interval_workload.c) builds its
error-free expansions from FMA residuals, and the README honestly
labels the augmented benefit a study model. Replace the stage-3
twoProduct/twoSum primitives with `msf64_augmentedMul` /
`msf64_augmentedAdd` (public API only, as now), re-deriving the
exactness guard for augmented semantics (clause-fixed rounding
toward zero; P1=R2 - an exact tiny residual is signaled but raises
no flag; only an unrepresentable mul residual raises
underflow+inexact). The containment contract is unchanged:
HIT/MISS/UNCERTAIN, never a wrong sign; capacity overflow still
yields UNCERTAIN. Sphere stage 3 only - box and torus untouched
unless a shared primitive forces a mechanical call-site rename.

Design entry first in `ledger/parcel-w6augint.md` (expansion
algebra with augmented pairs, guard derivation, op-count model
vs the FMA sequence) before code. Claim discipline: any
op-count delta is a measured record from the workload's own ops
counter over the frozen catalogue, never a performance claim.

**Owned files:** board/interval_workload.c, board/interval_workload.h,
board/interval_main.c and board/interval_host.c only if the call
or hash layout must move (prefer not), docs/metrics/briefs.jsonl
(own row, wave "wave6", base above). Library src/include frozen.
No RECORD/README edits - the lead records at merge.

**Acceptance:** (a) host catalogue run: stage-3 classifications
identical to the base implementation for every catalogue row
(run both, diff the full result stream, not a sample); (b) exact
expansion sums spot-checked against an exact oracle (Python
integers/Fractions over the same inputs) for a stated subset
including near-tangent rows; (c) ops totals before/after over
the catalogue recorded in your report; (d) existing negative-
control hooks still watched failing in scratch; (e)
`tools/run.sh standard` PASS in the worktree; (f) board run is
lead-only at the merge gate - do not flash anything.

**Outputs:** tip commit(s) on `wave6-augint` with detailed body +
`Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>`;
`scratch/parcel-w6augint/report.md` + `ledger/parcel-w6augint.md`.
Structured complete/evidence/unresolved mandatory. Script files,
Git Bash, MSF_PYTHON pinned to workspace .venv, scratch under
`scratch/parcel-w6augint/`, memory modest (no GB-scale sweeps;
state any ceiling). Nothing with `cft` in its name; no third-party
softfloat/math source as design input (executed oracles only).
~720 min.
