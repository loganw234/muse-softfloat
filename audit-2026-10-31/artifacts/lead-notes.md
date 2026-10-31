# Lead working notes (audit of muse-softfloat @ a2241fc, 2026-10-31)

## State
- Working dir /home/user/muse-softfloat is a SHALLOW clone (90 of 185 commits). Full bare mirror: SP/full.git (185 commits, 119 first-parent, branches main + wave6-ci/examples/sanitize all merged into main; no tags).
- SP = /tmp/claude-0/-home-user-muse-softfloat/f663923d-ec02-5a9b-9be5-2326751bedd2/scratchpad
- Agents (11) launched ~16:05 UTC; reports -> SP/agents/<name>/REPORT.md. IDs:
  oracle-diff a975e4ced10eb9b3f | exact-diff aff653542f56bf5ee | math-diff ab141d51412733bb7 | strings a40d4f03bcf28f911
  api-portability a5dfd2ac01f7afe3f | test-infra a5a8b107e2463fb2e | mutation a12fb1029834aac4d | docs-claims a15bb30cd039040c3
  security-code a4d6d802a9ba824a0 | legal-media-history a5107d4d590ee74eb | board-site abebe393749a73d02
- IMPORTANT: do not write the report into audit-bundle/ (frozen). Do not leave build/ in the working tree (I created build/smoke there; delete it at the end: /home/user/muse-softfloat/build, my own run output, gitignored).

## Lead-verified facts (own runs)
- Gates reproduced in a fresh clone (SP/clone) on Linux gcc 13.3/py3.13: smoke PASS 15s; standard PASS 38s; sanitize MSF_SANITIZE=full (ASan+UBSan) PASS 70s, all canaries caught; example-host PASS 4s. Numbers match README: 411,213 vectors; 1,117,504 standard extras; 5,505,024 aug-pool checks. Skips by name: ARM symbol scan (no arm-none-eabi-gcc), x87-compiler-refusal control (no mingw32). Logs: SP/runs/*.log
- GitHub Actions: last 13 runs on main (CI 4 jobs + Pages) all success incl. head a2241fc. 0 releases, 0 tags, 0 PRs, 0 issues.
- Berkeley pins: SoftFloat-3e.zip + TestFloat-3e.zip SHA-256 match docs/metrics/fetches.jsonl; built 8086-SSE at SP/oracle.
- Live Pages site byte-identical to HEAD site/ (index.html app.js style.css msf.wasm data.json ops.json vectors-sample.json).
- audit-bundle MANIFEST.sha256: 576 entries, all OK (sha256sum -c works even with CRLF manifest on GNU coreutils; README of bundle says to run it).
- git fsck --full clean on the mirror; 185 commits, 35 merges; single author/committer "Logan <Logan@improperaperture.com>"; 185/185 carry "Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>".
- Static analysis (src/): gcc -fanalyzer 0 warnings x10 TUs; clang --analyze 2 warnings both in msf_math.c log_core (garbage value via log_big_sq_ge_pow2 / big_top_bit) -> judged false positives: valgrind memcheck (--track-origins) 0 errors on explog-f64/f32, trig-f64, alg-f64, aug-f64, from/to-decimal-str; builds with -ftrivial-auto-var-init=pattern and =zero pass all 411,213 vectors. clang-tidy(bugprone,cert,misc,analyzer): 6 notes (3x implicit-widening-of-multiplication at msf_math.c:370/379/387 `abuf[2*n]`, 1 branch-clone at 1571, 2 = the analyzer ones). MSan runtime unavailable (libclang_rt.msan missing).
- ruff (E9,F) over 96 tracked .py: no syntax errors; 10 unused-local/import notes live, 10 in frozen bundle. shellcheck over 11 live .sh: 8 warnings (SC2155 x6, SC2034 x2).
- msf_math.c:112 clz32() returns (true clz - 1) for nonzero x (clz32(1)=30, clz32(0x80000000)=-1; clz32(0)=32); big_top_bit() thus returns a BIT LENGTH, -1 for zero; log_top_index() = bitlength-1. Comment at msf_math.c:1356 admits the convention. Hazard: misleading names. (Reproduced with /tmp/claude-0/clz_probe.c)
- PERF (host x86-64, loaded box, ratios matter; src SP/lead/bench/bench.c, built vs Berkeley softfloat.a): msf64_add 127ns vs bf 17.8 (7x); mul 100 vs 12.5 (8x); div 3757 vs 18.5 (~200x); sqrt 612 vs 25 (24x); fma 161 vs 26 (6x); f32 div 2702 vs 11.5 (235x); sin_pi 192ns, exp2 266, log2 992. Cause: div_core = bit-serial restoring division (~174 iterations of 128-bit shl/cmp/sub) msf64.c:220-230; sqrt_core = 61-iteration bit-by-bit search each with a 64x64->128 multiply msf64.c:262-267.
- Project's own number (demo/README.md:111-122): IAS15 figure-8 2,000 steps ~26M interposed ops; board 1.58 accepted steps/s @125MHz => ~21 min => ~49 us/op ~ 6,000 cycles/op average; SF-0 sec 8 quotes ROM _fadd 71 / _ddiv 183 cycles and sets a WORKING BUDGET "basic binary64 ops within 2x of ROM averages when RAM-resident, core static RAM zero, stack measured per op class, flash per format" as goals; no result for those budgets found in README/RECORD/BOARD (grep). README only says "counted records, not timing claims".
- Headline claim nuance: SF-0 sec 9 defines "unmodified desktop run" as THE SAME EXTRACTED SUBSET (~750-950 lines, variational/collision/forces branches deleted on both sides), strict flags (-std=c99 -ffp-contract=off, -O3 for inline sqrtsd), figure-8 3-body, 2,000 steps; demo/README.md:91-96 says a contracting (default FMA) build diverges at step 1. README headline ("bit-identical to the unmodified desktop run — same integrator source") omits these qualifiers.
- Owner waived the clean-room fingerprint audit (KICKOFF.md:196-198) -> clean-room vs the cft reference is a waiver, not a completed audit; kit zip sha256 still unconfirmed (KICKOFF.md:98-99, adherence report D10).
- Project's own prior audit: audit-bundle/reports/audit-adherence-final/report.md ("ADHERENT WITH SLIPS", frozen @bc807e6) lists debts D1-D15 (false universals README:141-144 [check if still present], corrections.jsonl frozen at 16 rows, 65 plants rows checked_by=integration, key-hash pre-commitment adopted only in Wave 6...).
- GitHub demo URLs (REBOUND/KissFFT archives) return 403 via this container's proxy => README step 4 (demo/run_demo.sh host) NOT reproduced here (limit, not defect).

## Agent findings ledger (fill as reports arrive)
(see FINDINGS-LEDGER.md)
