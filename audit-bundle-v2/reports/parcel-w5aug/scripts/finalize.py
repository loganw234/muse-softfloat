import pathlib
ws = pathlib.Path(__file__).resolve().parents[3]
rp = ws/"scratch/parcel-w5aug/report.md"
t = rp.read_text()
lines = t.splitlines()
lines[0]="READY"
# replace stale header block (lines 1-5ish) keep rest, then replace Not started + scope sections
t="\n".join(lines)+"\n"
t=t.replace("P1 = R2 ratified (see entry gate). P4 = fixed. P5 = internal\nmode value 5. Entry gate COMPLETE; seam slice, kernel, and\nevidence NOT STARTED in this run. No kernel code written, no\nbuild/test/team gates run. Details and the full as-to-be-shipped\nflag table: ledger/parcel-w5aug.md.",
"P1=R2 (exact tiny residual raises NO flag), P4=fixed, P5=internal RTTZ mode 5. Branch wave5-aug (worktrees/w5-aug), base bce49e0, 3 commits: 2c89edd seam, 0ecdd11 kernel, 3741453 evidence. Tier2 66/66, 849 instantiations. Flag table as shipped = ledger/parcel-w5aug.md entry-gate table (implemented in src/msf_aug.c from exact-residual tests).")
# cut stale sections
idx=t.find("## Not started / not done")
if idx>=0: t=t[:idx]
t+=("""## Final evidence (2026-10-29 continuation)

- Exhaustive binary16 pairs (one-time, 256 shards/op, ulimit -v 262144 KB, BelowNormal, counts printed in logs/exh-summary-{add,sub,mul}.txt): add 4,294,967,296 PASS 0 mismatches (751s); sub 4,294,967,296 PASS 0 (758s); mul 4,294,967,296 PASS 0 (704s, incl. mul-inexact-tail 1,258,291,200; tiny-exact/P1 cells add/sub 754,232,664 each, mul 487,736,456). Kind sums check to 2^32 each.
- Fresh final gates this run: smoke PASS 24s (logs/final-smoke.log), standard PASS 54s incl. standing pool 5,505,024 0 mismatches (logs/final-standard.log). Study-reference crosscheck: 20,640 cases 0 disagreements (logs/crosscheck.log).
- Earlier this parcel (logs retained): regen twice byte-stable; vectors aug-f16 46,088 / f32 46,146 / f64 46,146 directed+seeded (RTTZ ties, overflow tie+above, verbatim, zero signs, P1 cells, mul below-step, NaN/inf x2); six mutants refused (te-head 5478, zero-tail-sign 30727, swap-pair 105583, jam-window 30458, p1-opposite 14558, pack-leak 39626 fails; control PASS 138380); ARM -Os and -O3 clean; board build-only links, host-replay fake-serial pair PASS + corrupt refused.

## Not done

- On-silicon board replay: lead work (no flashing per brief).
- Interval workload integration: not this parcel; op-count benefit remains the study's measured model, not a shipped claim.
""")
rp.write_text(t)
lp = ws/"ledger/parcel-w5aug.md"
lt = lp.read_text()
lt += """
## Results (2026-10-29, append-only)

READY, merge-ready on wave5-aug, not pushed/merged. Commits:
2c89edd seam (aug_pair sig, 9 rows C-754 project-exact flags-yes
rounding fixed, pair header + msf64 hidden-pointer ABI note,
two-result runner/trampoline, board pair reply, run.sh counts,
regen twice byte-stable, smoke with rows planned); 0ecdd11
kernel (src/msf_aug.c exact window + verbatim branch, RTTZ
mode 5 in msf_roundpack.c, WIDTHS proof incl. binade-crossing);
3741453 evidence (house-style project-exact reference,
directed/seeded vectors 46,088/46,146/46,146, f16 harness).
Final: smoke PASS, standard PASS (pool 5,505,024, 0 mismatches);
exhaustive f16 pairs 2^32 per op x3, 0 mismatches, counts in
scratch/parcel-w5aug/logs/exh-summary-{add,sub,mul}.txt; six
mutants refused; ARM -Os/-O3 clean. Full report:
scratch/parcel-w5aug/report.md. Open: on-silicon replay (lead),
interval integration (not this parcel).
"""
lp.write_text(lt)
print("ok")
