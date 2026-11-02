# Verifier report: Wave 2 binary16 parcel (copy `worktrees/verify2-f16`, HEAD `9a414ec`, parent `dd48b08`)

Verdict: **NOT READY**. Three wrong-answer defects in `src/msf16.c` (div ×2 incl. flags, div missing divisionByZero, sub inf-sign) plus one wrong committed expectation and two stale committed vector files send work back. All other probes pass.

Machine under third-party load throughout; wall times are records, never rates. Clean-room kept: never opened/searched/listed anything with `cft` in it; never touched `scratch/lead/`, the parcel branch, or key files; copy unmodified (git status clean apart from `build/`).

## Findings (one per line; class a = regression/claim-surface deviation, b = wrong answer)

- (b) div exponent+1: every finite-finite `msf16_div*` quotient is 2x too large (all 9 instantiations: homogeneous + 8 cross-format dest=f16). Smallest repro: `msf16_div te 3c00 3c00 -> 3c00 00` got `4000/00`. Berkeley L1 te alone: 36378 value mismatches / 46464; all 5 modes fail ~36.5k-36.7k.
- (b) div missing divisionByZero: finite nonzero / +-0 returns +-inf with flags 00, want 02. Smallest repro: `msf16_div te 4b7f 0000 -> 7c00 02` got `7c00/00`. 333 such flag-only mismatches in L1 te (all y=+-0, x finite nonzero); 0/0 and inf/inf invalid paths are correct.
- (b) sub infinity sign flipped: finite minus +inf returns +inf (want -inf); finite minus -inf returns -inf (want +inf). Smallest repro: `msf16_sub te 0 7c00 -> fc00 00` got `7c00/00`. Berkeley L1: exactly the 345 x-vs-inf cases per mode fail (all 5 modes); every non-inf sub case passes.
- (b) committed `tests/vectors/arith-f16.vec` line 5 has a wrong expectation: `msf16_add te 0 3c00 -> bc00` (claims 0+1=-1); implementation returns `3c00` (correct) and the current generator emits `3c00`. Regenerate the file.
- (a) committed `tests/vectors/arith-f16.vec` does not regenerate byte-identically (1 line: above).
- (a) committed `tests/vectors/conv-int-f16.vec` does not regenerate byte-identically (12 lines, 3 hunks, e.g. `msf16_from_u16 te ffd0 -> 7bfe 10` committed vs `msf16_from_u16 te ffc0 -> 7bfe 00` regenerated). Both sides arithmetically correct; the generator's directed input set moved after the commit. Regenerated file replays 1144/1144 PASS, so the implementation is fine on both sets.

## Probes (counts; skips named)

1. Budgets: `tools/run.sh smoke` PASS in 14s (52168 vectors, drift byte-identical, type scan clean, symbol scan clean, all 9 negative controls refused incl. planned-only). `tools/run.sh standard` PASS in 34s (smoke 52168 + f16-exhaustive 917504 + pack-sweep 200000 = 1117504). Nothing skipped.
2. Claim surface vs base `dd48b08`: 12 files changed, all parcel-owned (`src/msf16.c`, `tests/gen_vectors_f16.py`, 6 new `tests/vectors/*f16*.vec`) or regenerated (`docs/COVERAGE.tsv`, `include/muse_softfloat.h`, `tests/msf_dispatch.h` all byte-identical to fresh `tools/gen_tables.py` output). `tables/implemented.tsv` grows 417 -> 653 lines (+236, append-only, no `-` lines). No off-limits file touched. Skipped: none.
3. Committed directed replay (smoke-built runner): arith-f16 3880/4320 (440 fails = F-div/F-sub/F-add-line above); compare-f16 2802/2802; conv-int-f16 1144/1144; fma-sqrt-f16 1674/1674; rint-misc-f16 985/985; toint-f16 1840/1840. Regeneration to temp: compare/fma-sqrt/rint-misc/toint byte-identical; arith DIFF (1 line); conv-int DIFF (12 lines). Skipped: none.
4. Berkeley differential (`testfloat_gen.exe` pinned 3e build, `MSF_TESTFLOAT_GEN` set): level 1 complete, every applicable mode — add 46464x5 PASS; mul 46464x5 PASS; sqrt 408x5 PASS; rem 46464 PASS (value+flags exact under nan-class); fma 6133248x5 PASS; rint 408x5 PASS; from_f32 600x5, from_f64 768x5, from_i/u32 372x5, from_i/u64 756x5, to-int 408x20 (berkeley-int compare) all PASS; comparisons 46464x6 PASS; sub 46119/46464x5 (345 inf-sign fails); div ~9750-9910/46464x5 (rest fail per F-div/F-DZ). from_f16: NO Berkeley generator exists (ingest writes 0 cases, all 5 modes) — covered instead by exhaustive probe 6 (65536x5 PASS vs independent reference). Level 2 `--take 2000000`: add/mul te+tz (1254528 cases each, stream smaller than take) PASS; sqrt te+tz (2448 each) PASS. Skipped with reason: div/sub L2 (same root causes already fail L1, rerun adds no information); fma L2 (L1 already 6.1M cases/mode, dwarfs a 2M take); rem/rint/conv/cmp L2 (L1 slices complete per the Berkeley matrix); tp/tn/ta takes (time; te+tz discriminate).
5. Independent exact reference (fresh `scratch/verifier-w2f16/ref_f16.py`, Fraction/integer arithmetic, no generator imports; two of my own bugs found and fixed mid-probe: ties-to-away semantics, rint negative-zero sign): edge-exact 144/156 (12 fails all subsumed by F-div incl. tininess-boundary div cases); edge-nanclass 36/36 PASS (arithmetic NaN propagation incl. sNaN invalid); ta-probe 35/35 (ties-to-away confirmed correct); tininess at 0x0001, NaN truncate-to-default (f32 0xFFC12345 -> 0xFE09 etc.), signed zeros incl. tn rules, remainder ties (incl. 5.5/2 -> -0.5), totalOrder negative-NaN payload-descending, scaleB non-integral N (2.5 -> truncate to 2) and huge-N saturation with pack flags, logB incl. subnormal leading zeros — all agree. Skipped: NaN-N scaleB (language-defined, untested by design).
6. Exhaustive unary f16->f16, all 65536 encodings vs reference: from_f16 x5 modes 65536/65536 PASS; sqrt x5, rint x5+named, rint_exact, next_up, next_down 64514/65536 each with the 1022 fails in every file being sNaN inputs only (implementation quiets to default 0x7E00+invalid; reference passes payload through; allowed NaN-propagation choice, nan-class accepts, finite/zero/inf/qNaN all agree). Skipped: none.

## Cross-checks that raise confidence in the verdict

- Three-way agreement on remainder substance: my reference matches Berkeley on all 44020 non-invalid rem values; implementation matches Berkeley on all 46464 under nan-class (mismatches ref-vs-Berkeley are NaN-payload/sign delivery only, flags agree).
- My reference totalOrder key matches all 800 committed totalOrder/totalOrderMag expectations (implementation passed them too).
- Regenerated conv-int file (new inputs) passes 1144/1144 against the implementation.

## Not done

- No board budget (out of scope for this brief).
- L2 takes listed as skipped in probe 4 with reasons.
- No clause escalation was needed; the only ambiguity met (NaN payload propagation, scaleB NaN N) is allowed/language-defined, recorded as notes not findings.
- Wall times: smoke 14s, standard 34s, full Berkeley L1 sweep dominated by fma (30.7M cases) within one extended run; see per-file logs in `scratch/verifier-w2f16/`.

Evidence files: `smoke.log`, `standard.log`, `probe2-drift.log`, `probe3-replay.log`, `probe3-regen.log`, `regen-gen.log`, `berk1-arith.log`, `berk1-rint.log`, `berk1-conv.log`, `berk1-cmp.log`, `edge-exact.log`, `edge-nanclass.log`, `ta-probe.log`, `exhaust-replay.log`, `ref_f16.py`, `gen_edge.py`, `gen_taprove.py`, `gen_exhaust.py`, `xcheck.py`, all under `scratch/verifier-w2f16/`.
