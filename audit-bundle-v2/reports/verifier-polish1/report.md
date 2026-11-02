NOT READY — 4 findings (F1, F2 parcel-introduced; F4 parcel-introduced; F3 pre-existing but explicitly gated by the parcel brief).

Scope: copy `worktrees/verify-polish1` (HEAD `fa8a27a`) vs parent `400b271`. Never consulted the parcel branch, other worktrees, keys, `scratch/lead/`, `ledger/lead.md`, or `docs/metrics/plants.jsonl`. All runs below executed in a duplicate at `scratch/verifier-polish1/dup` (Git Bash, `MSF_PYTHON` = workspace `.venv` python); the copy was never modified (read-only probes: `ffmpeg -i` banners, `git show/diff`, file reads).

## Findings (claimed vs re-derived)

F1 — README video master wrong file's specs (parcel-changed claim).
Claimed: `README.md:102-104` — "The current silent cut is the 180-second, 1920x1080 `video/out/assembly_v5.mp4`".
Re-derived: `ffmpeg -i` banner on the copy's `video/out/assembly_v5.mp4` reads Duration 00:02:49.00 (= 169.0 s), 2560x1440. The 180-second/1920x1080 figures describe `video/out/final.mp4` (banner: 00:03:00.00, 1920x1080). Corroborated by the parcel's own files: `video/README.md:7` (169.0 s, 2560x1440), `video/assemble.py:31-37` (SEGMENTS 7.0+22.5+29.0+102.0+8.5 = 169.0), measured segment banners matching the table. `README.md:13` ("169-second") contradicts `README.md:102`.

F2 — committed `site/data.json` plants headline neither reproduces nor sums.
Claimed: `site/data.json:68` — `"caught": 120, "total": 120`.
Re-derived: rerunning `site/build_data.py` in the duplicate prints `plants=114/120` and writes `caught: 114`; `ops.json` equal, `vectors-sample.json` byte-equal, `data.json` otherwise identical except `base` (environment label, see probes). The committed `by_wave` rows (unchanged by the rerun) sum to 9+10+5+25+46+9+10 = 114 caught / 120 total. `README.md:48` ("114 of 120 plants caught") and the parcel evidence ("plants 114/120") agree with 114, contradicting the committed headline 120. Per `site/build_data.py:204-206` the headline is a whole-file `grade=="caught"` count, so 120 cannot arise from the same inputs that yield the committed `by_wave`.

F3 — BOARD TWIDDLES link target missing (pre-existing, parcel-gated).
Claimed (parcel brief gate): "BOARD TWIDDLES link resolves".
Re-derived: `docs/BOARD.md:145` links `[docs/TWIDDLES.md](../TWIDDLES.md)`; from `docs/` that resolves to repo-root `TWIDDLES.md`, which does not exist (the file lives at `docs/TWIDDLES.md`). Present identically at parent `400b271:137`, so not parcel-introduced, but the parcel brief's own gate requires it to resolve and the parcel did not fix it.

F4 — BOARD clone LED pins swapped (parcel-added claim).
Claimed: `docs/BOARD.md:40-43` (new 2026-10-28 block) — clones' activity LED is "a PIO-driven WS2812 on GP25 (the Pico uses GP16)".
Re-derived: `board/msf_led.h:17-19` — Pico uses `PICO_DEFAULT_LED_PIN` (GP25) GPIO, clones use WS2812 on GP16 (`MSF_LED_WS2812_PIN 16u`, line 42); corroborated by the pre-existing `docs/RECORD.md:863-866` ("GP25 GPIO for the Pico, a PIO-driven WS2812 on GP16 for the Zeros"). The new BOARD text has the two pins exactly swapped.

## Clean re-derivations (claim == tree)

- Serials: BOARD's five clone serials + genuine `e66440a2cb6f5c2b` match `RECORD.md:850-856` exactly.
- Attributes: header enum (`muse_softfloat.h:76-81`) has 5 rounding modes; `msf_math.c:2-3` "all four … the fifth, roundTiesToAway" reconciles; COVERAGE `rounding==attr` rows = 273, matching `README.md:36`.
- Citations: all 9 `audit-bundle/ledger/parcel-*.md` paths cited in `src/`+`tools/` exist in `audit-bundle/ledger/` (f16, f32, f64, w4trig, w5alg1, w5alg2, w5aug, w5exp2, w5log2); no stale bare-`ledger/` citations remain in `src/`/`tools`/`include`.
- CMakeLists: comment (`board/CMakeLists.txt:48-49`, "none is registered") matches the file — only the empty `compiler` flavour is selected, no flavour library target exists.
- `video/out/` contents all present; STORYBOARD v5 section (`:223`, 169.0 s/1440p, 58.5–160.5/160.5–169.0 boundaries) matches measured banners.

## Probes run

1. Claim surface (`git diff 400b271..HEAD`, 24 files): every changed present-tense claim re-derived — see findings + clean list above.
2. `tools/gen_tables.py` rerun in duplicate: all four outputs (`include/muse_softfloat.h`, `src/msf_formats.h`, `tests/msf_dispatch.h`, `docs/COVERAGE.tsv`) byte-identical to the copy's (comp OK ×4); decimal comment at header `:114` matches generator in both.
3. `site/build_data.py` rerun in duplicate: `ops.json` equal, `vectors-sample.json` byte-equal (320,779 B), `data.json` differs only in `plants.caught` (120 committed vs 114 re-derived) and `base` (`400b271` = generation-time HEAD label vs `fa8a27a` in the duplicate — environmental, not a finding). Internal sums: by_wave totals sum to 120 ✓, caught sums to 114 ✗ vs headline 120 (F2). Inventory cross-check: COVERAGE data rows 849 (783 tier1 + 66 tier2, attr 273) vs data.json 849/783/66 ✓; vectors total 411,213 ✓ both.
4. `bash tools/run.sh smoke` in duplicate: PASS in 23 s — drift check clean, unit 849 instantiations, `total 411213 passed 411213 failed 0`, inventory tier1 783/783 + tier2 66/66/0 planned, all 12 negative controls refused.
5. Video commands: every `video/README.md` render command names an existing `video/*.py` script; STORYBOARD `:215`/`:242` and `probe.py:5` `..\..\.venv` paths resolve under the documented `<workspace>/muse-softfloat` + root-`.venv` layout (case-insensitive on this machine); all four segment `Run:` self-names match real filenames (no stale `render_*` names); segment outputs (`intro3`/`outro3` from `intro_outro.py`, `idea2-1440p.mp4`, `why3-1440p.mp4`, `gitvisual5.mp4` default `--out`) match `assemble.py` ORDER; durations sum 169.0 ✓ and match measured banners. Live check: `probe.py out/proof.mp4` from `video/` → 26.5 s, h264, 1920x1080, 30.0 fps, 795/795 frames, rc 0 — matches `video/README.md:103-105`.
6. RECORD appendix: `git diff --numstat` shows `docs/RECORD.md` 13+/0− (appendix-only ✓); `briefs.jsonl` 31 rows at parent (incl. Step 3a row, none dropped) + 1 polish row = 32, all parse; `498a916` (adds the `parcel-w5exp2` row) is an ancestor of HEAD ✓.

## Not done

- Nothing required left undone: all six brief probes ran. `standard` gate not required by this brief (parcel evidence cites it; only `smoke` was required and it passed).
- Observation (out of scope, unchanged by parcel, not a finding): `demo/twiddle_gate.c:6` cites `ledger/parcel-w4kissfft.md` without the `audit-bundle/` prefix, and no such file exists in `audit-bundle/ledger/` — outside the parcel's owned files and probe 1's `src/`+`tools/` scope.
