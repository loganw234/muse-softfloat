#!/usr/bin/env python3
"""Draw the bench-record graphs from the retained raw board logs.

Reads the two raw logs named on the command line (defaults: the
parcel-psbench2 retained logs under scratch/), recomputes every
median from the per-repetition BENCH-REP lines and cross-checks
it against the firmware's BENCH summary lines, then writes:

  docs/img/bench_compare.png - binary32/binary64 add/mul/fma/
      div/sqrt, muse-softfloat beside the stock SDK routines,
      bench-pico run, log scale.
  docs/img/bench_library.png - every library row, both SDK
      flavours, log scale.

These are pictures of the records in docs/BENCH.md (medians of 5
repetitions on the labelled runs); they make no performance
claim. Output is deterministic for fixed input logs: fixed
figure sizes/DPI, fixed row order, pinned PNG metadata, so a
rerun on the same logs reproduces the PNGs byte-identically.

Usage: bench_graphs.py [bench2-pico.log] [bench2-compiler.log]
"""
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "docs" / "img"

BG = "#0b1020"
PANEL = "#0b1020"
TEXT = "#e5e7eb"
MUTED = "#9ca3af"
CYAN = "#22d3ee"    # muse-softfloat
AMBER = "#f59e0b"   # stock SDK
INDIGO = "#818cf8"  # second flavour in the library graph

REP_RE = re.compile(
    r"^BENCH-REP name=(.*) rep=\d+ iters=\d+ total_us=\d+ "
    r"ns_per_op=\d+ cycles_per_op_x100=(\d+) sink=[0-9a-f]{16}$")
SUM_RE = re.compile(
    r"^BENCH name=(.*) reps=\d+ iters=\d+ median_total_us=\d+ "
    r"median_cycles_per_op_x100=(\d+) min_cycles_per_op_x100=\d+ "
    r"max_cycles_per_op_x100=\d+ sink=[0-9a-f]{16}$")

COMPARE = [
    ("f32 add", "msf32_add", "sdk32_add"),
    ("f32 mul", "msf32_mul", "sdk32_mul"),
    ("f32 fma", "msf32_fma", "sdk32_fma"),
    ("f32 div", "msf32_div", "sdk32_div"),
    ("f32 sqrt", "msf32_sqrt", "sdk32_sqrt"),
    ("f64 add", "msf64_add", "sdk64_add"),
    ("f64 mul", "msf64_mul", "sdk64_mul"),
    ("f64 fma", "msf64_fma", "sdk64_fma"),
    ("f64 div", "msf64_div", "sdk64_div"),
    ("f64 sqrt", "msf64_sqrt", "sdk64_sqrt"),
]
LIBRARY_ROWS = [
    "empty_loop",
    "msf16_add", "msf16_mul", "msf16_fma", "msf16_div", "msf16_sqrt",
    "msf32_add", "msf32_mul", "msf32_fma", "msf32_div", "msf32_sqrt",
    "msf64_add", "msf64_mul", "msf64_fma", "msf64_div", "msf64_sqrt",
    "msf32_exp2", "msf32_log2", "msf32_sin_pi",
    "msf64_exp2", "msf64_log2", "msf64_sin_pi",
    "msf32_from_i32", "msf64_to_i32_ties_to_even", "msf32_from_f64",
    "msf16_class", "msf32_is_signaling", "msf64_copy_sign",
    "msf_pack_f64(exemplar)",
]


def default_logs():
    names = ("bench2-pico.log", "bench2-compiler.log")
    roots = [REPO / "../scratch/parcel-psbench2/raw",
             REPO / "../../scratch/parcel-psbench2/raw",
             Path.cwd() / "scratch/parcel-psbench2/raw",
             Path.cwd() / "../scratch/parcel-psbench2/raw"]
    for r in roots:
        r = r.resolve()
        if all((r / n).is_file() for n in names):
            return [r / names[0], r / names[1]]
    raise SystemExit("raw logs not found; pass both log paths as arguments")


def parse_log(path):
    labels, reps, sums = {}, {}, {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line.startswith("LABEL "):
            k, _, v = line[6:].partition("=")
            labels[k] = v
            continue
        m = REP_RE.match(line)
        if m:
            reps.setdefault(m.group(1), []).append(int(m.group(2)))
            continue
        m = SUM_RE.match(line)
        if m:
            sums[m.group(1)] = int(m.group(2))
    medians = {}
    for name, summary in sums.items():
        vals = sorted(reps.get(name, []))
        assert len(vals) == 5, f"{path.name}/{name}: {len(vals)} reps"
        assert vals[2] == summary, (
            f"{path.name}/{name}: recomputed median {vals[2]} "
            f"!= summary {summary}")
        medians[name] = summary / 100.0
    return labels, medians


def fmt_val(v):
    return f"{v:,.0f}" if v >= 100 else f"{v:.2f}"


def style_ax(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=10)
    for s in ax.spines.values():
        s.set_color("#334155")
    ax.title.set_color(TEXT)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)


def save(fig, name):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / name
    fig.savefig(out, dpi=150, facecolor=BG,
                metadata={"Title": name, "Software": "tools/bench_graphs.py"})
    plt.close(fig)
    print("wrote", out)


def draw_compare(labels, med):
    groups = [g[0] for g in COMPARE]
    msf = [med[g[1]] for g in COMPARE]
    sdk = [med[g[2]] for g in COMPARE]
    x = np.array([0, 1, 2, 3, 4, 6, 7, 8, 9, 10], dtype=float)
    w = 0.38
    fig, ax = plt.subplots(figsize=(11.5, 6.4))
    fig.patch.set_facecolor(BG)
    style_ax(ax)
    b1 = ax.bar(x - w / 2, msf, w, color=CYAN, label="muse-softfloat (full IEEE 754 semantics)")
    b2 = ax.bar(x + w / 2, sdk, w, color=AMBER, label="stock SDK routines")
    ax.set_yscale("log")
    ax.set_ylim(80, 400000)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:,.0f}"))
    ax.set_ylabel("median cycles per operation (log scale)")
    ax.set_xticks(x)
    ax.set_xticklabels(groups, color=TEXT)
    ax.grid(axis="y", color="white", alpha=0.12, linewidth=0.6)
    ax.set_axisbelow(True)
    for bars in (b1, b2):
        for rect in bars:
            ax.annotate(fmt_val(rect.get_height()),
                        (rect.get_x() + rect.get_width() / 2, rect.get_height()),
                        textcoords="offset points", xytext=(0, 3),
                        ha="center", fontsize=8.5, color=TEXT)
    ax.set_title("Cycles per operation on RP2040 @ 125 MHz (median of 5, log scale)\n"
                 "full IEEE 754 semantics vs stock SDK routines",
                 fontsize=13, pad=12)
    leg = ax.legend(frameon=False, fontsize=10, loc="upper left")
    for t in leg.get_texts():
        t.set_color(TEXT)
    fig.text(0.01, 0.005,
             "Built for exactness, not speed: these are records of the labelled bench-pico run, "
             "not performance claims.\n"
             f"Source: docs/BENCH.md (run of {labels.get('date', '?')}, genuine Pico "
             f"{labels.get('board_serial_target', '?')}, git {labels.get('git_head', '?')[:12]}); "
             "full loop-body cost, operand generation included, no overhead subtraction.",
             fontsize=7.5, color=MUTED)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.86, bottom=0.13)
    save(fig, "bench_compare.png")


def draw_library(labels_a, med_a, labels_b, med_b):
    rows = list(reversed(LIBRARY_ROWS))  # table order top-to-bottom
    va = [med_a[r] for r in rows]
    vb = [med_b[r] for r in rows]
    y = np.arange(len(rows), dtype=float)
    h = 0.38
    fig, ax = plt.subplots(figsize=(11.5, 12.0))
    fig.patch.set_facecolor(BG)
    style_ax(ax)
    b1 = ax.barh(y + h / 2, va, h, color=CYAN, label="bench-pico (pico default flavour)")
    b2 = ax.barh(y - h / 2, vb, h, color=INDIGO, label="bench-compiler (compiler flavour)")
    ax.set_xscale("log")
    ax.set_xlim(8, 1200000)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:,.0f}"))
    ax.set_xlabel("median cycles per operation (log scale)")
    ax.set_yticks(y)
    ax.set_yticklabels(rows, color=TEXT, fontsize=9.5, family="monospace")
    ax.grid(axis="x", color="white", alpha=0.12, linewidth=0.6)
    ax.set_axisbelow(True)
    for bars in (b1, b2):
        for rect in bars:
            ax.annotate(fmt_val(rect.get_width()),
                        (rect.get_width(), rect.get_y() + rect.get_height() / 2),
                        textcoords="offset points", xytext=(4, 0),
                        va="center", fontsize=8, color=TEXT)
    ax.set_title("muse-softfloat library rows on RP2040 @ 125 MHz\n"
                 "median cycles per operation of 5 repetitions, log scale, both SDK flavours",
                 fontsize=13, pad=12)
    leg = ax.legend(frameon=False, fontsize=10, loc="lower right")
    for t in leg.get_texts():
        t.set_color(TEXT)
    fig.text(0.01, 0.004,
             "Records of the labelled runs in docs/BENCH.md, not performance claims; full loop-body cost, "
             "operand generation included.\n"
             f"bench-pico run of {labels_a.get('date', '?')}; bench-compiler run of {labels_b.get('date', '?')}; "
             f"genuine Pico {labels_a.get('board_serial_target', '?')}, git {labels_a.get('git_head', '?')[:12]}.",
             fontsize=7.5, color=MUTED)
    fig.subplots_adjust(left=0.235, right=0.965, top=0.945, bottom=0.055)
    save(fig, "bench_library.png")


def main():
    args = sys.argv[1:]
    if len(args) == 2:
        logs = [Path(args[0]), Path(args[1])]
    elif len(args) == 0:
        logs = default_logs()
    else:
        raise SystemExit("usage: bench_graphs.py [bench2-pico.log bench2-compiler.log]")
    labels_a, med_a = parse_log(logs[0])
    labels_b, med_b = parse_log(logs[1])
    for _, lib, sdk in COMPARE:
        assert lib in med_a and sdk in med_a, f"missing row in {logs[0].name}"
    for r in LIBRARY_ROWS:
        assert r in med_a and r in med_b, f"missing library row {r}"
    draw_compare(labels_a, med_a)
    draw_library(labels_a, med_a, labels_b, med_b)
    return 0


if __name__ == "__main__":
    sys.exit(main())
