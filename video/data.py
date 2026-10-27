"""Load REAL project data (read-only) for charts, counters and tickers.

Sources, all inside this repository (or its parent workspace in the original layout):
  docs/metrics/passes.jsonl  one row per agent pass (tool_uses, times)
  docs/metrics/usage.jsonl   one row per agent (token counts)
  docs/metrics/plants.jsonl  one row per planted defect (grade caught/missed)
  git log                    commit subjects for the ticker
Headline constants are traced (SOURCES below) to docs/RECORD.md entries,
README.md, tools/run.sh, and the IAS15 hash files in scratch, so a number
on screen is never invented here. Every constant was re-verified at its
source for the final cut (2026-10-27); the wave a figure was counted at is
part of its source string wherever a later count is not recorded.
"""
from __future__ import annotations

import json
import struct
import subprocess
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if (HERE.parent / "docs" / "metrics").exists():
    REPO = HERE.parent                                  # published: <repo>/video
    ROOT = REPO.parent                                  # original workspace, if present
else:
    ROOT = HERE.parent                                  # original: <workspace>/video
    REPO = ROOT / "muse-softfloat"
METRICS = REPO / "docs" / "metrics"
VIDEO_DATA = HERE / "data"

# Traceable headline numbers. Value -> where a human can check it.
SOURCES = {
    "instantiations": "muse-softfloat/docs/RECORD.md Wave 3: '783 of 783 instantiations implemented' (+ README.md Status)",
    "smoke_vectors": "muse-softfloat/docs/RECORD.md Wave 3: 'added the string sets to smoke (85,148 committed vectors)'",
    "standard_vectors": "muse-softfloat/docs/RECORD.md Wave 1: 'standard adds 1,117,504'; same figure re-printed at Wave 3 close (ledger/lead.md 2026-10-27 10:32: 'smoke 85,148 + 1,117,504 standard, 9/9 controls') - on-screen '(Wave 1 count)' is conservative",
    "berkeley_cases": "muse-softfloat/docs/RECORD.md Wave 1: 'combined post-fix Berkeley evidence exceeds 37M cases' (say exceeds, never exact)",
    "f16_fma": "muse-softfloat/docs/RECORD.md Wave 2: 'f16 fma 6.1M x 5 modes', Berkeley L1 complete",
    "f16_exhaustive": "muse-softfloat/docs/RECORD.md Wave 2: 'exhaustive 65,536-encoding unary sweeps'",
    "plants": "muse-softfloat/docs/metrics/plants.jsonl (counted at load time); RECORD: Wave 1 9/10, Wave 2 10/10, Wave 3 5/5 = 24/25",
    "negative_controls": "muse-softfloat/tools/run.sh controls(): 9 named controls, 'negative controls: all refused'; RECORD Wave 1 '9/9 negative controls refused'",
    "tininess": "muse-softfloat/docs/RECORD.md Wave 1: Clause 7.5 tininess defect in lead kernel + Python reference, Berkeley disagreed, fixes 53acb1a/b37fb12, Spark recheck 'oracle differential 2400/2400', ingest eq 46,464-case proof",
    "board_w1": "muse-softfloat/docs/RECORD.md Wave 1: 2,767 sampled vectors, SHA-256 4d7c2a28... identical host/board, RP2040 ID e66440a2cb6f5c2b; 'sample, not full-volume replay'",
    "board_w2": "muse-softfloat/docs/RECORD.md Wave 2: 2,489 sampled f16/xf vectors, SHA-256 729f495d... host == board; Wave 3: same sample re-replayed on the final tree, hash identical",
    "aeabi_selftest": "muse-softfloat/docs/RECORD.md Wave 3: 'AEABI selftest passes on the RP2040 (47,107 checks)'",
    "ias15": "muse-softfloat/docs/RECORD.md Wave 3 + ledger/lead.md 2026-10-27 09:44: 2,001 IAS15FH1 records match desktop exactly (matched=2001); digests in scratch/ias15/out/hashes_native.txt == worktrees/w-ias15/build/ias15-board/hashes_board.txt (re-compared at render)",
    "ias15_rate": "ledger/lead.md 2026-10-27 09:44: RATE block_steps=1000 elapsed_us=631495596 = 1.58 accepted steps/s at clk_sys 125 MHz; full period t=6.33 = 944 steps ~ 10 min ('the video treats as time-lapse', RECORD Wave 3)",
    "fig8_ics": "scratch/ias15/work/ic_fig8.txt (binary64 bit patterns, G=1, N=3, Chenciner-Montgomery figure-8); orbit frames integrate these exact ICs in Python float64 and are labelled an illustration",
    "bootrom": "muse-softfloat/docs/RECORD.md Wave 0 (survey S3): bootrom flushes output denormals to zero, input denormals as zero, NaNs as infinities, no exception flags; SDK fma unfused, fmaf double-rounding",
    "rounding": "muse-softfloat/docs/RECORD.md Wave 0 (survey S1): four binary rounding attributes, ties-to-away operations required; decimal conversions correctly rounded to H >= 20 (project H=20, RECORD Wave 3)",
}
HEADLINE = {
    "implemented": 783,
    "total_instantiations": 783,
    "smoke_vectors": 85148,
    "standard_vectors": 1117504,
    "berkeley_cases_label": "37M+",
    "board_hash": "729f495d3e92bcd82931bd42b237705ad5333fe3ffeba4f5e3b39b0b2583f2b9",  # W2 sample, re-replayed W3
    "board_hash_w1": "4d7c2a28581a36381d4ccf5084f3e909b68e186a763d45341c48ced427b329af",
    "board_vectors_w1": 2767,
    "board_vectors_w2": 2489,
    "aeabi_checks": 47107,
    "board_id": "e66440a2cb6f5c2b",
    "ias15_records": 2001,
    "ias15_steps": 2000,
    "ias15_period_steps": 944,
    "ias15_rate_label": "1.58 steps/s at 125 MHz",
}


def _ias15_hashes(path: Path) -> dict[int, tuple[str, str]]:
    rows: dict[int, tuple[str, str]] = {}
    for ln in path.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            f = ln.split()
            rows[int(f[0])] = (f[1], f[2])     # (H_state, H_full)
    return rows


def ias15_digests() -> dict:
    """Desktop vs board IAS15FH1 digests, re-compared at load time.

    Desktop and board captures ship beside this file in data/ for the
    published repository. In the original workspace layout, fall back to
    scratch/ias15/out/hashes_native.txt and the w-ias15 worktree capture.
    The step-0/2000 prefixes asserted below pin the files to RECORD Wave 3.
    """
    native_path = VIDEO_DATA / "hashes_native.txt"
    if not native_path.exists():
        native_path = ROOT / "scratch" / "ias15" / "out" / "hashes_native.txt"
    native = _ias15_hashes(native_path)
    assert len(native) == 2001, len(native)
    assert native[0][0].startswith("62bb23b0") and native[0][0].endswith("333e01")
    assert native[2000][0].startswith("4d4530a6") and native[2000][0].endswith("f48abb")
    board_path = VIDEO_DATA / "hashes_board.txt"
    if not board_path.exists():
        board_path = ROOT / "worktrees" / "w-ias15" / "build" / "ias15-board" / "hashes_board.txt"
    matched = None
    if board_path.exists():
        board = _ias15_hashes(board_path)
        matched = sum(1 for k, v in native.items() if board.get(k) == v)
        assert matched == 2001, matched
    return {"native": native, "board_matched": matched,
            "steps_shown": [0, 944, 2000]}


# Figure-8 initial conditions as binary64 bit patterns, copied from
# scratch/ias15/work/ic_fig8.txt (x y vx vy per particle, m=1, G=1). The
# orbit scene integrates these in float64 as a labelled illustration of the
# proven-identical IAS15 run; positions cannot be decoded from hashes.
_FIG8_BITS = [
    (0x3FEF0A469565AD59, 0xBFCF1D7DFFB52C72, 0x3FDDD647FB166140, 0x3FDBABE14F90B6F2),
    (0xBFEF0A469565AD59, 0x3FCF1D7DFFB52C72, 0x3FDDD647FB166140, 0x3FDBABE14F90B6F2),
    (0x0000000000000000, 0x0000000000000000, 0xBFEDD647FB166140, 0xBFEBABE14F90B6F2),
]
FIG8_T_FINAL = 12.651827085113784   # t_final of the 2,000-step run, compare.log


def fig8_ics() -> list[tuple[float, float, float, float]]:
    return [tuple(struct.unpack("<d", struct.pack("<Q", b))[0] for b in row)
            for row in _FIG8_BITS]


def _jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def load_passes() -> list[dict]:
    return _jsonl(METRICS / "passes.jsonl")


def load_usage() -> list[dict]:
    return _jsonl(METRICS / "usage.jsonl")


def load_plants() -> list[dict]:
    return _jsonl(METRICS / "plants.jsonl")


def tool_uses_by_agent(limit: int = 8) -> list[tuple[str, int]]:
    """Top agents by summed tool_uses across passes.jsonl (real, computed)."""
    tot: dict[str, int] = defaultdict(int)
    for r in load_passes():
        tot[str(r.get("agent", "?"))] += int(r.get("tool_uses") or 0)
    return sorted(tot.items(), key=lambda kv: -kv[1])[:limit]


def output_tokens_by_agent(limit: int = 8) -> list[tuple[str, int]]:
    tot: dict[str, int] = defaultdict(int)
    for r in load_usage():
        tot[str(r.get("agent", "?"))] += int(r.get("output_tokens") or 0)
    return sorted(tot.items(), key=lambda kv: -kv[1])[:limit]


def cumulative_tool_uses() -> list[tuple[str, int]]:
    """(end-time, running total of tool_uses) in chronological order."""
    rows = [r for r in load_passes() if r.get("end")]
    rows.sort(key=lambda r: str(r["end"]))
    out, run = [], 0
    for r in rows:
        run += int(r.get("tool_uses") or 0)
        out.append((str(r["end"]), run))
    return out


def plant_score() -> tuple[int, int]:
    rows = load_plants()
    caught = sum(1 for r in rows if str(r.get("grade")) == "caught")
    return caught, len(rows)


_PLANT_GROUP_LABELS = {
    "verifier-w1f32": "W1 f32", "verifier-w1f64": "W1 f64",
    "verifier-w2f16": "W2 f16", "verifier-w2xf": "W2 xf",
    "verifier-w3str": "W3 str",
}


def plant_groups() -> list[tuple[str, list[str]]]:
    """(label, grades) per verifier, in plants.jsonl file order."""
    groups: list[tuple[str, list[str]]] = []
    for r in load_plants():
        label = _PLANT_GROUP_LABELS.get(str(r.get("verifier")),
                                        str(r.get("verifier", "?")))
        if not groups or groups[-1][0] != label:
            groups.append((label, []))
        groups[-1][1].append(str(r.get("grade")))
    return groups


def git_subjects(limit: int = 40) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(REPO), "log", f"-{limit}", "--pretty=%h  %s"],
        capture_output=True, text=True, check=True,
    )
    return [ln for ln in out.stdout.splitlines() if ln.strip()]


def summary() -> dict:
    caught, total = plant_score()
    return {
        "passes_rows": len(load_passes()),
        "usage_rows": len(load_usage()),
        "plants_caught": caught,
        "plants_total": total,
        "tool_uses_by_agent": tool_uses_by_agent(),
        "output_tokens_by_agent": output_tokens_by_agent(),
        "cumulative_tool_uses_final": cumulative_tool_uses()[-1][1],
        "git_subjects": git_subjects(12),
        "plant_groups": plant_groups(),
        "ias15_board_matched": ias15_digests()["board_matched"],
        "ias15_step0_hstate": ias15_digests()["native"][0][0],
        "ias15_step2000_hstate": ias15_digests()["native"][2000][0],
        "fig8_ics": fig8_ics(),
        "headline": HEADLINE,
        "sources": SOURCES,
    }


if __name__ == "__main__":
    print(json.dumps(summary(), indent=2))
