#!/usr/bin/env bash
# Interim commits on wave5-log2 (never push/merge).
set -eu
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w5-log2
git add tables/implemented.tsv include/muse_softfloat.h docs/COVERAGE.tsv \
    tests/msf_dispatch.h src/msf_explog_tables.h tools/gen_explog_tables.py \
    src/msf_math.c tests/explog_decider.c tests/explog_exhaustive.c
git commit -m "SF-2 Step 3b: log2/log2p1 kernel, generator Ek, decider extension" \
-m "Correctly rounded log2/log2p1 at binary16/32/64 per the design entry in ledger/parcel-w5log2.md (written before kernel code): exact wide w formation (x, or 1+x) in a 40-limb big, exact mm^2>=2 recentring square compare, s=(mm-1)/(mm+1) by the new floor-exact bit-by-bit wf_div from separately normalized NUM/DEN bigs (log2p1 wide-span truncation charged as the s-division sticky Ek line at 2eps per conversion under the shipped bit-length big_top_bit convention, probe-verified), atanh series, integer composition k+(t+-Ek) materialised exactly at pack scale deciding the power-of-two attractor tail, log2p1 tiny-|x| relative path, poles exact. Exact results are exactly the powers of two (log2 of a dyadic is an integer or irrational: tie set empty, kernel inexact by proof), specials per Clause 9.2 extracts. Generator extended (bracket-floored 1/ln2, 2/ln2; 1/(2j+1), 1/(j+1) entries; EK_LOG {146,242,370}, EK_TINY {147,243,371}; exp values unchanged, regen byte-stable). Decider/harness extended not forked (fn ids 2/3, MPFR adaptive bracket on mpfr_log2/mpfr_log2p1, independent table for specials/domain/powers). Registration: Tier 2 57 implemented of 57. Evidence so far: f16 exhaustive all-4 PASS (1,310,720 checks, final_undecided 0), f64 wc 100% both functions PASS, seeded PASS; f32 exhaustive, negatives, smoke/standard, target rerun follow on this frozen kernel." \
-m "Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>"
git add tests/gen_vectors_explog.py tests/vectors/explog-f16.vec \
    tests/vectors/explog-f32.vec tests/vectors/explog-f64.vec \
    tests/VECTORS.md docs/WIDTHS.md docs/metrics/briefs.jsonl
git commit -m "SF-2 Step 3b: committed log2/log2p1 vectors + doc rows" \
-m "Vector generator extended to four functions (exp Step-3a lines byte-prefix preserved, verified): log families specials/powers/sqrt2/near1/tiny/lattice/pole/sticky/domain/hardest/seeded, 90,315 expectation lines total, ta independently decided, specials+powers cross-checked against the generator's Fraction settled table (generation refuses on disagreement), regeneration twice byte-identical. VECTORS.md provenance rows, WIDTHS.md kernel row, briefs.jsonl row for parcel-w5log2." \
-m "Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>"
git --no-pager log --oneline -3
git status --porcelain
