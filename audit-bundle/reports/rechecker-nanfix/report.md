# rechecker-nanfix report: 5-line `msf_nan_to_dest` fix at 4cdb912

Stance: disconfirm-only. Target: `4cdb912dbd5ebda4fa2bc29168883dc4527d4091`
(parent `de2d48c`, pushed and READY-verified; not re-verified wholesale).
Workspace `C:\Users\logan\source\repos\Muse-Softfloat`, repo `muse-softfloat/`.
Scope: verifier-w1prep note N1 (unreachable truncate-to-default branch).
Verdict: **READY** — zero (a), zero (b), 3 notes (none blocking).

Counts: diff parent..target is exactly the claimed fix, nothing else
(1 file, 3+/2-); NaN probe 236/236 agree with an SF-0 2.5 field-arithmetic
reference on the fixed code, 19/19 pre-fix failures all N1-class on the
parent header; `tools/run.sh smoke` 29982/29982 PASS, 9/9 controls refused;
commit-message claims all hold; `git status` clean, board untouched, no
`cft` names anywhere in scratch work.

## 0. Environment (all in scratch/rechecker-nanfix/, tree untouched)

- `git -c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat`
  for every git read. HEAD is 4cdb912, `git status --short` empty after all work.
- mingw64 gcc 16.1.0 via Git Bash with `mingw64/bin` first on PATH and
  TMPDIR/TMP/TEMP pointed into scratch (sandbox denies the default Local\Temp;
  direct PowerShell invocation dies in cc1, Git Bash recipe works).
- Probe `nanprobe.c` (one source, `-Wall -Wextra` clean) built twice: `-I
  muse-softfloat/src` (fixed, `nanprobe-new.exe`) and `-I old/` where `old/`
  holds parent-revision headers extracted via `git show de2d48c:...`
  (`nanprobe-old.exe`; `msf_internal.h`/`msf_formats.h`/`include/muse_softfloat.h`
  verified byte-identical between parent and target by the empty name-only
  diff outside `src/msf_decode.h`).
- One mid-course probe bug of my own, fixed and disclosed: corpus entry
  `1u << (frac_bits-1)` is UB for f64 (practically `0x80000`, still a legal
  tiny-payload case); now `1ULL`. And delivery check (7) first used a quiet
  NaN where only a signaling NaN can truncate to zero (section 2) — the
  reference and the fixed code agreed against my hardcoded expectation;
  split into (7a)/(7b).

## 1. Probe (1): the diff is exactly the claimed fix, nothing else

`git diff de2d48c..4cdb912 --stat`: `src/msf_decode.h | 5 +++--`
(3 insertions, 2 deletions). Full diff is the hunk moving the
`dpayload == 0u` default-qNaN return above `dpayload |= df->quiet_bit`:

    -    dpayload |= df->quiet_bit;
    -    if ((dpayload & df->frac_mask) == 0u) {
    +    if (dpayload == 0u) {
    +        /* payload truncated away entirely: default quiet NaN (2.5) */
             return df->default_qnan;
         }
    +    dpayload |= df->quiet_bit;
         return (src->sign ? df->sign_mask : 0u) | df->infinity | dpayload;

Unreachability proof of the old branch (code reading + constants in
`src/msf_formats.h`): old code ORs `quiet_bit` first; quiet_bit is
`0x0200`/`0x00400000`/`0x0008000000000000` for f16/f32/f64, each inside the
matching `frac_mask`, so `(dpayload & frac_mask)` could never be zero.
No other file differs. No (a), no (b).

## 2. Probe (2): NaN probe vs own SF-0 2.5 reference — 236 checks

Reference `ref_nan_to_dest` is independent field arithmetic written from
the SF-0 2.5 matrix text (`docs/studies/SF-0.md` section 2.5: payload
shifts left on widening, right with truncation on narrowing; narrowing
that truncates the payload to zero delivers the destination default quiet
NaN — positive, quiet bit set, rest zero; otherwise sign preserved and
quiet bit set; signaling inputs quieted under item (b)).

Coverage, all 9 (src,dest) pairs over {f16,f32,f64} x both signs:
10-payload corpus (1, 2, 3, quiet>>1, quiet, quiet|1, full mask,
mask>>1, top payload bit, 0xDEAD-masked), plus the exact truncation
boundary per narrowing pair (largest payload still truncating to zero and
smallest surviving: shifts 13/29/42), plus real qNaN/sNaN encodings
through `msf_decode` both signs, plus 8 `msf_nan_delivery` checks
(sNaN-priority, first-sNaN-wins, quiet-first no-invalid, invalid-without-NaN
default+invalid, quiet return-0 untouched, FMA inf/zero/qNaN-addend split,
negative signaling truncate-to-zero, negative quiet narrowing).

- Fixed code: `NANPROBE: checks=236 mismatches=0 n1class=0` (`out-new.txt`).
- Pre-fix header: `checks=236 mismatches=19 n1class=19`, and zero FAIL
  lines outside the N1 class (`out-old.txt`). Every one is negative sign +
  payload truncating to zero: got sign-preserved minimal quiet NaN
  (`0xfe00` for f16 dest, `0xffc00000` for f32 dest), want positive
  default (`0x7e00` / `0x7fc00000`). Positive truncate-to-zero cases pass
  on old code too (identical bits), exactly as the commit message says.

Refinement note N1-R (spec reading, not a finding): the truncate-to-zero
branch is reachable only through signaling inputs — a quiet NaN's top
(quiet) bit always survives a right shift, so `dpayload == 0u` requires
the quiet bit to be clear. The observable pre-fix defect class is
therefore exactly: negative sNaN, payload entirely below the narrowing
shift, delivered sign-preserved instead of positive-default. The fix
handles the whole class; nothing else changes behavior (236-case
old-vs-new agreement everywhere outside the class is implied by
new=236/236 plus old failures confined to the class).

Verdict probe (2): no (a), no (b).

## 3. Probe (3): run.sh smoke PASS

`tools/run.sh smoke` at 4cdb912 under Git Bash (`smoke.log`):
`total 29982 passed 29982 failed 0 malformed 0 skipped-planned 0`,
`VERDICT: PASS`, `budget smoke: PASS in 8s`, 9/9 negative controls
`refused as required`, symbol scan clean. Matches the parent's
29982/29982 count from the verifier-w1prep report (parent smoke not
re-run here; count inherited as believed, section 5). Commit claim
"smoke PASS unchanged" HOLDS.

## 4. Probe (4): commit-message accuracy — every sentence holds

- Title "Fixed unreachable truncate-to-default NaN branch
  (verifier-w1prep N1)": accurate — section 1 proof, and N1's text
  (unreachable condition, sign-preserved `0xffc00000` observed) reproduced
  on the parent header by my probe (got `0xfe00`/`0xffc00000`).
- "ORed the quiet bit before testing for a fully truncated payload":
  exact (diff, section 1).
- "a payload that shifts to zero delivered a sign-preserved minimal
  quiet NaN instead of the destination's positive default quiet NaN
  that SF-0 2.5 specifies": measured (section 2); SF-0 2.5's
  narrowing rule and default-qNaN definition READ in
  `muse-softfloat/docs/studies/SF-0.md` lines 207-223.
- "The zero test now precedes the quiet-bit OR.": exact (diff).
- "No caller exists yet (Wave 1 parcels are first);": HOLDS —
  `msf_nan_to_dest`/`msf_nan_delivery` appear only in `src/msf_decode.h`
  itself (definitions + the two internal delivery call sites); no hits
  in `src/*.c`, `include/`, `tools/`, `tests/`, `board/`, `compat/`.
- "smoke PASS unchanged.": HOLDS (section 3).
- "Scoped Spark recheck gates the push.": true by construction (this task).

## 5. Classification and what was not done

- (a) regressions: none — 0 lines.
- (b) wrong answers: none — 0 lines.
- Notes: N1-R (truncate-to-zero reachable only via sNaN inputs;
  refines N1, no action); method note (mid-course probe fixes in
  section 0, both disclosed); parent smoke count inherited from the
  verifier-w1prep report, not re-run (cheap, unchanged-tree count match).
  None blocks the push.
- Ledger: entry appended via kit `tools/ledger.sh` (or staged body —
  see reply).
- Did NOT do: re-verify parent de2d48c wholesale; touch the board (no
  serial/lock interaction); rebuild firmware; run `board`/`bench`
  budgets; modify any project file (`git status` clean); use any file
  with `cft` in its name (none in scratch, ledger, or repo reads);
  spawn background work (nothing running).
