# verifier-w5site report — copy `worktrees/verify5-site` (HEAD `1e6722d`, parent `a0acf2a`)

NOT READY

Five disconfirming findings: (1) flag chips swap UNDERFLOW/INEXACT vs the
header; (2) page status line claims plant score 80/80, the repo says 75/80
(stale `data.json` top level; the page's own by-wave table sums to 75);
(3) page claims exp2/log2/augmented "landed" but COVERAGE has zero such
rows and RECORD has no such landing at this base; (4) root README live-URL
href uses `muse_softfloat` (underscore), every other reference uses
`muse-softfloat`; (5) KissFFT panel calls the workload "unmodified:",
which RECORD forbids ("never described as unmodified KissFFT" — it is
patched at exactly three sites). WASM honesty itself verified: 1,596
vectors replayed through the copy's `site/msf.wasm` under Node, 0
mismatches; tie pair and flag probes correct against the header.

## Environment

- Git Bash, `python` = Miniconda 3.12.15, `node` = v22.19.0, Edge
  156.0.4314.50 headless. Single-threaded throughout. Copy never modified;
  all mutation happened in `scratch/verifier-w5site/{regen,degraded}`.
- Scripts: `scratch/verifier-w5site/recount.py`, `probes.mjs`,
  `deal-shim.mjs`, `regen.sh`, `degraded.sh`, `final.sh`.

## Replay / probes (all observed, not repeated from the parcel)

- `node worktrees/verify5-site/site/replay.mjs worktrees/verify5-site/site`
  → `msf_op_count=828 ops_json=828 sample=1596`, `replayed=1596
  mismatches=0`.
- `node scratch/verifier-w5site/probes.mjs` → 5/5 OK against
  `include/muse_softfloat.h` bit values: f32 te tie `1.0+2^-24 →
  0x3f800000 flags=0x10`; ta → `0x3f800001 flags=0x10`; `1/0 → inf
  flags=0x02`; fmax×2 → inf `flags=0x14`; hypot(3,4)=5 flags=0.
- Flag chips (`site/app.js:11-14`) vs header
  (`include/muse_softfloat.h:70-74`): header UNDERFLOW=0x08,
  INEXACT=0x10; page maps 0x08→"inexact", 0x10→"underflow". **Swapped.**
  The overflow probe above (flags=0x14) would light "underflow" instead
  of "inexact" in the page.

## Per-claim trace

| # | Claim / requirement | Verdict | Evidence |
|---|---|---|---|
| 1 | WASM honesty: bundled sample replays clean | PASS | Self-run: 1596 replayed, 0 mismatches (above) |
| 2 | te/ta tie pair behaves | PASS | Probes: te→0x3f800000, ta→0x3f800001, both flags 0x10 |
| 3 | Flag-raising op honest | PASS | div-by-zero flags=0x02, overflow flags=0x14, match header |
| 4 | Flag chips match `muse_softfloat.h` | **FAIL (F1)** | app.js 0x08=inexact/0x10=underflow vs header 0x08=UNDERFLOW/0x10=INEXACT |
| 5 | 828 instantiations (783 Tier 1 + 45 Tier 2), all implemented | PASS | `recount.py`: COVERAGE 828 rows, tier 783/45, implemented 828; matches `data.json` |
| 6 | 182,518 committed vectors | PASS | Recounted 182,518 lines; per-file map matches `data.json` exactly |
| 7 | 80 plant rows, by-wave table | PASS (table) | `plants.jsonl`: 80 rows; waves wave1 9/10, wave2 10/10, wave3 5/5, wave4 25/25, wave5 17/20, readme 9/10 — matches page table |
| 8 | Status-line plant score 80/80 | **FAIL (F2)** | File says 75 caught; `data.json` top-level `caught:80` is stale (generator prints `plants=75/80`); page status line inherits it while its own table sums to 75 |
| 9 | IAS15 facts (2001/2001, 4d4530a6, 1.58/s @125MHz, 1000-step block, ~10 min) | PASS | `index.html:121-125` matches `docs/RECORD.md` Wave-3 entry verbatim in substance ("unmodified desktop build" wording is RECORD's own) |
| 10 | Interval facts (710/710, ce81d66e, 7.92 s) | PASS | `index.html:137-139` matches RECORD Step-2b entry |
| 11 | KissFFT facts (131.2.0 BSD-3 scratch-only, 12/12, N=256/1024/4096, named change) | PASS in substance, **FAIL wording (F5)** | `index.html:145` writes "unmodified:"; RECORD says patched at exactly three sites, "never described as unmodified KissFFT" — and the next sentence contradicts itself |
| 12 | exp2/log2/augmented labelled in-progress | **FAIL (F3)** | `index.html:179-180` says "Now also landed"; `COVERAGE.tsv` has 0 such rows, `ops.json` has 0, RECORD at base has no such landing |
| 13 | rSqrt/hypot/roundTiesToAway landed | PASS | Covered by RECORD Wave-5 Step 1/2a/2b; Tier 2 45/45 consistent |
| 14 | Degraded mode labels recorded results as recorded | PASS | Real exercise: scratch copy with `msf.wasm` renamed, headless Edge → banner `wasm-status down`: "shows recorded results ... labelled as recorded — no live computation"; real `app.js` deal branch via shim → "Recorded result shown", result kind `U16 (recorded)`, Run disabled |
| 15 | pages.yml uploads `site/` correctly | PASS | `path: site`, permissions contents-read/pages-write/id-token-write, trigger on `site/**`, Actions deploy route |
| 16 | README live URL == repo Pages address | **FAIL (F4)** | Root `README.md` link target `https://loganw234.github.io/muse_softfloat/` (underscore); repo is `github.com/loganw234/muse-softfloat`, parcel spec + `site/README.md` + page repo-line all use hyphen `muse-softfloat`; link text itself says hyphen while href says underscore |
| 17 | Internal links resolve | PASS | Anchors #instrument/#numbers/#silicon/#verification match section ids; style.css/app.js/data.json/ops.json/vectors-sample.json/msf.wasm all present |
| 18 | No external requests | PASS | Grep: no `http` in app.js/style.css/glue.c/replay.mjs/build.py/build_data.py; no `url(` in CSS; only user-clicked github.com doc anchors in index.html |
| 19 | Regeneration byte-identical | PARTIAL — data.json stale (F2) | Scratch `build_data.py` rerun: `ops.json` identical, `vectors-sample.json` identical, `data.json` differs only in `base` (scratch checkout reports "unknown", environmental) and `plants.caught` 80→75 (real staleness) |
| 20 | Claim surface == parent + owned files | PASS | `git diff a0acf2a..HEAD --stat`: only `site/**` (13 files + wasm), `pages.yml`, README link line, `docs/metrics/briefs.jsonl` row; `src/ tests/ tables/` untouched |

## Findings (file refs)

- F1 (behavior): `site/app.js:11-14` FLAG_DEFS swaps UNDERFLOW/INEXACT
  vs `include/muse_softfloat.h:70-74`. Any inexact-only result (e.g. the
  verified tie, flags=0x10) lights the "underflow" chip.
- F2 (stale generated file): `site/data.json` `plants.caught: 80`;
  `docs/metrics/plants.jsonl` has 75 caught of 80 and the file's own
  `by_wave` sums to 75. Regeneration produces 75. Page status line
  (`app.js:311`) therefore reads "80 of 80" while the plants table on the
  same page reads 75/80.
- F3 (false landing claim): `site/index.html:179-180` "Now also landed:
  the exp2/log2 pairs and Clause 9.5 augmented arithmetic" — at base
  `a0acf2a` there are no such COVERAGE rows, no such dispatch ops, and no
  RECORD landing. Must read in-progress.
- F4 (wrong link): root `README.md` live-demo href uses underscore
  `muse_softfloat`; correct Pages address for repo `muse-softfloat` is
  `https://loganw234.github.io/muse-softfloat/` (as the parcel ledger,
  `site/README.md`, and the page's own repo-line all state).
- F5 (forbidden wording): `site/index.html:145` "unmodified:" for KissFFT;
  governing rule (parcel ledger + RECORD) is never "unmodified" — the
  workload is patched at exactly three sites. Self-contradicted by the
  following sentence.

## Not done

- `msf.wasm` rebuild from source not rerun (no zig/clang wasm toolchain on
  this box; explicitly skippable for load; `build.py --skip-replay` path
  untested for the same reason).
- Pages workflow never run (needs push + owner Pages enablement); live URL
  404s until then — owner action at merge, already documented in
  `site/README.md` and pages.yml comments.
- No pixel/screenshot QA (Edge `--dump-dom` worked; screenshot not
  attempted).
- Non-Edge browsers unchecked.
- Root `README.md` Status section still carries pre-parcel stale figures
  (822/822, 171,423 vectors, 61/65 plants) — parent's text, outside the
  parcel's owned files; noted, not charged to this parcel.
