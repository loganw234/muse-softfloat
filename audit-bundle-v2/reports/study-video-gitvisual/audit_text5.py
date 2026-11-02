"""v5 text audit: every on-screen text block vs THE RULE.

Imports v4 + v5 renderers (single source of truth for copy), measures
cursor-paced dwells (sendback / branch labels) by inverting
cursor_rank, and writes audit_text5.json. Word = whitespace token;
a 64-hex check-value or a big number counts as 1 token (it is read
as one chunk, and it is the real artefact on screen).
Window blocks: dwell given = 7.2 - appear_lt (readable until the
window starts closing), except PASS whose specified hold is the
1.5 s to window end (6.5 -> 8.0).
"""
import json
from pathlib import Path
import render_gitvisual4 as V4
import render_gitvisual5 as V5

HERE = Path(__file__).resolve().parent
wc = V5.word_count
rule = V5.rule_dwell

def t_of_cursor(R, target, lo, hi):
    prev_t, prev_v = lo, R.cursor_rank(lo) - target
    t = lo
    while t < hi:
        t += 0.02
        v = R.cursor_rank(t) - target
        if prev_v <= 0 <= v and not (prev_v == 0 == v):
            a, b = prev_t, t
            for _ in range(60):
                m = (a + b) / 2
                if R.cursor_rank(m) < target:
                    a = m
                else:
                    b = m
            return (a + b) / 2
        prev_t, prev_v = t, v
    return hi

def block(scene, name, text, dwell_given, appear_note=""):
    w = wc(text)
    need = rule(w)
    return {"scene": scene, "block": name, "text": text, "words": w,
            "dwell_given_s": round(dwell_given, 2), "rule_min_s": need,
            "ok": dwell_given >= need - 1e-9, "note": appear_note}

rows, totals = [], {"v4": 0, "v5": 0}

# ---- chase popups ----
for i, node in enumerate(V5.NODES):
    old = node["title"] + " " + " ".join(node["lines"]) + " " + V4.SHORT_SRC[i]
    totals["v4"] += wc(old)
    t5, lines5 = V5.POPUP5[i]
    new = t5 + " " + " ".join(lines5)
    totals["v5"] += wc(new)
    rows.append(block("chase", f"popup {i} {node['id']}", new, V5.POPUP_DWELL[i],
                      f"v4: {wc(old)}w @2.3s (rule {rule(wc(old))}s)"))
    for ln in lines5:
        assert wc(ln) <= 10, ln
    assert wc(t5) <= 6

# chase persistent: legend + strip + scene src tag
legend = "LEGEND - SYSTEMS " + " ".join(V5.DEEP)
totals["v4"] += wc(legend); totals["v5"] += wc(legend)
rows.append(block("chase", "legend (unchanged)", legend, V5.T_BRIDGE - 1.0))
old_strip = "1 - THE CHASE: the trail lights each system | chase camera in 3D - marbles split at branches"
new_strip = "1 - THE CHASE | marbles split at branches"
totals["v4"] += wc(old_strip); totals["v5"] += wc(new_strip)
rows.append(block("chase", "bottom strip", new_strip, V5.T_BRIDGE - 6.5,
                  "phase word swaps at lift; longest phase shown"))
totals["v5"] += wc(V5.SRC_CHASE)
rows.append(block("chase", "scene src tag", V5.SRC_CHASE, V5.T_BRIDGE - 1.0))

# ---- sendbacks (cursor-paced; measured) ----
V5.assign_lanes(); V4.assign_lanes()
for sb5, sb4 in zip(V5.SENDBACKS, V4.SENDBACKS):
    old = sb4["label"] + " " + sb4["sub"] + " src: " + sb4["src"] + " SENDBACK - FIXED - REJOIN"
    new = sb5["label"] + " " + sb5["sub"]
    totals["v4"] += wc(old); totals["v5"] += wc(new) + wc("FIXED - REJOINS")
    apex5 = sb5["rank"] - 1.0 + V5.sb_apex_frac(sb5) * V5.LOOP_SPAN
    # visible dwell: apex -> end of dim tail (rank+18 = drawn-window edge),
    # minus any gate-window overlap (label hides while a gate is up)
    t_a = t_of_cursor(V5, apex5, V5.T_REPLAY, V5.T_BOX)
    t_b = t_of_cursor(V5, sb5["rank"] + V5.SB_LABEL_TAIL + V5.SB_LABEL_DIM,
                      V5.T_REPLAY, V5.T_BOX)
    d5 = t_b - t_a - sum(max(0.0, min(t_b, g["t1"]) - max(t_a, g["t0"]))
                         for g in V5.GATES)
    apex4 = sb4["rank"] - 1.0 + V4.sb_apex_frac(sb4) * V4.LOOP_SPAN
    d4 = (t_of_cursor(V4, sb4["rank"] + 5.0, 31.0, 79.0)
          - t_of_cursor(V4, apex4, 31.0, 79.0))
    rows.append(block("replay", f"sendback rank {sb5['rank']:.0f}", new, d5,
                      f"visible apex->rank+{V5.SB_LABEL_TAIL + V5.SB_LABEL_DIM:.0f} "
                      f"(readable then dimmed, gate overlap removed); "
                      f"v4: {wc(old)}w @{d4:.2f}s (rule {rule(wc(old))}s)"))
    rows.append(block("replay", f"sendback badge rank {sb5['rank']:.0f}",
                      "FIXED - REJOINS", d5))

# branch labels: worst-case dwell over the 25 lanes (1-token names)
worst = None
for m in V5.MERGES:
    if m["target"] != "main":
        continue
    a = t_of_cursor(V5, float(m["merge_base_rank"]), V5.T_REPLAY, V5.T_BOX)
    b = t_of_cursor(V5, min(float(m["rank"]) + 16.0, float(V5.LAST_RANK)), V5.T_REPLAY, V5.T_BOX)
    if worst is None or b - a < worst[0]:
        worst = (b - a, m["branch"])
rows.append(block("replay", "branch labels x25 (worst lane)", worst[1], worst[0],
                  "1-token data labels; dwell = lane label window"))
day = block("replay", "day separators", "10-27", 8.0,
            "1 token; on screen while its rank crosses the 66-rank window (>=8 s worst leg)")
rows.append(day)

# ---- gate windows (lt-based) ----
WIN_END = 7.2
def win(scene, name, text, appear_lt, old_text, old_appear):
    totals["v4"] += wc(old_text); totals["v5"] += wc(text)
    rows.append(block(scene, name, text, WIN_END - appear_lt,
                      f"appear lt={appear_lt}; v4: {wc(old_text)}w "
                      f"@{WIN_END - old_appear:.1f}s (rule {rule(wc(old_text))}s)"))

for g5, g4 in zip(V5.GATES, V4.GATES):
    win(g5["id"], "title+sub", g5["title"] + " " + g5["sub"], 0.0,
        g4["title"] + " " + g4["sub"], 0.0)
    rows.append(block(g5["id"], "scene src tag", g5["src"], WIN_END))
win("window", "boards header", "SIX BOARDS (mockup)", 0.8,
    "SIX BOARDS (1 Pico + 5 Zero) - mockup", 0.0)
for s in ("RP2040", "Pico - GP25 LED", "RP2040-Zero - WS2812"):
    totals["v4"] += wc(s); totals["v5"] += wc(s)
rows.append(block("window", "board labels (names)", "Pico - GP25 LED", WIN_END))
totals["v4"] += wc("PASS - all six LEDs hold solid"); totals["v5"] += 1
rows.append(block("window", "PASS", "PASS", 1.5, "specified 1.5 s hold, 6.5->8.0"))

# IAS15 viz
win("ias15", "orbit caption", "figure-8 orbit (picture)", 0.0,
    "figure-8 orbit (illustration)", 0.0)
win("ias15", "orbit sub", "real start, drawn on desktop", 0.5,
    "real ICs, integrated in float64", 0.0)
win("ias15", "hash title", "state check-values: desktop == chip", 0.4,
    "IAS15FH1 H_state: desktop == RP2040", 0.0)
for k, st in enumerate(V5.IAS15["steps_shown"]):
    rows.append(block("ias15", f"hash row step {st}",
                      f"STEP {st:,} <64-hex> desktop == RP2040", WIN_END - (0.4 + k * 1.0 + 0.8),
                      "hash = 1 token"))
    totals["v5"] += 6; totals["v4"] += 6
win("ias15", "proof line", "check-values at right are the proof", 1.6,
    "positions cannot be decoded from hashes - the hash rows at right are the proof", 0.0)
win("ias15", "stamp", "2,001 / 2,001 IDENTICAL desktop == chip", 3.5,
    "2,001 / 2,001 RECORDS BIT-IDENTICAL ON SILICON", 5.2)
win("ias15", "chip line", "IAS15 on the chip, via muse-softfloat", 4.0,
    "IAS15 on RP2040 via muse-softfloat (AEABI surface) src: video/data.py SOURCES[ias15]; RECORD Wave 3", 0.0)

# KissFFT viz
win("kissfft", "caption", "sound wave in, spectrum out", 0.0,
    "waveform -> twiddles -> spectrum", 0.0)
win("kissfft", "honesty line", "(picture only - not KissFFT output)", 0.0,
    "(illustration; spectrum via numpy - NOT KissFFT output)", 0.0)
totals["v4"] += wc("shared LCG input, N=256 complex fwd (cfg 0)")  # v5: dropped
win("kissfft", "twiddle caption", "exact twiddle factors", 2.7,
    "exact-fraction twiddles e^-2pik/N", 0.0)
win("kissfft", "stamp", "12 / 12 SETUPS CHECKED check-values recorded", 3.6,
    "12 / 12 CONFIGURATIONS - HASHES RECORDED src: scratch/study-kissfft-visual/report.md", 6.3)
win("kissfft", "spectrum caption", "spectrum, bin by bin", 4.5,
    "magnitude spectrum builds bin by bin", 0.0)

# tokens viz
win("tokens", "top line", "recounted at a73e97d", 0.0,
    "REGENERATED at a73e97d - definition below; v1 number retired (stale)", 0.0)
rows.append(block("tokens", "big number", "1,196,128,770", WIN_END - 2.4,
                  "counts up 0->2.4, then holds"))
totals["v4"] += 1; totals["v5"] += 1
win("tokens", "definition", "billed = input + output (93 rows)", 0.6,
    "project billed = input + output, 93 labeled rows (usage.jsonl)", 0.0)
win("tokens", "in/out lines",
    "input 1,190,490,305 + output 5,638,465 cached 1,165,653,139 sits inside input", 1.2,
    "input 1,190,490,305 (cached 1,165,653,139 inside input) + output 5,638,465", 0.0)
win("tokens", "owner caption", "you typed ~1,928 tokens (amber, to scale)", 1.8,
    "owner-typed ~1,928 tokens (chars/4, frozen study est.) - amber tick is to scale", 0.0)
win("tokens", "final lines", "~1 : 620,399 - 7,756 messages your share: 0.00016%", 2.6,
    "~1 : 620,399 - human share 0.00016% - 7,756 logged msgs "
    "src: regen_gate2.py <- usage.jsonl @ a73e97d; owner: study-tokens-visual", 4.8)
win("tokens", "zoom head", "x500,000 ZOOM YOU: ~1,928 tokens", 3.2,
    "x500,000 ZOOM (drawn parametrically) YOU: ~1,928 tokens [1,350-2,507]", 3.2)
win("tokens", "zoom line 3", "40 prompts, 7,713 characters", 4.2,
    "40 owner prompts - 7,713 chars (study, frozen)", 3.2)

# ---- HUD / box ----
hud_old = ("2 - THE REPO, AS IT HAPPENED (marble track) replay: Wave 0-3 > IAS15 window "
           "into main NEWEST ^ (up-stream) OLDEST v (behind) close angled window on real "
           "topology (history.json) | green = merge | red loop = sendback/fix | marbles split + rejoin")
hud_new = ("2 - AS IT HAPPENED next: IAS15 window NEWEST ^ OLDEST v " + V5.SRC_REPLAY
           + " | green = merge | red loop = fix")
totals["v4"] += wc(hud_old); totals["v5"] += wc(hud_new)
rows.append(block("replay", "HUD title/key/src", hud_new, V5.T_BOX - V5.T_REPLAY,
                  "persistent; commit ticker excluded (data readout, see report)"))
box_old = "3 - BOXED every system files its colours away - then the lid shuts marbles in: 7 / 7 kept: RECORD - ledgers - vectors - metrics muse-softfloat RECORD LEDGERS VECTORS METRICS"
box_new = "3 - BOXED every system packed away marbles in: 7 / 7 muse-softfloat RECORD LEDGERS VECTORS METRICS"
totals["v4"] += wc(box_old); totals["v5"] += wc(box_new)
# marble name labels (7 system names; already counted in the legend total)
for name, txt in (("box title", "3 - BOXED"), ("box sub", "every system packed away"),
                  ("box counter", "marbles in: 7 / 7"),
                  ("box front name", "muse-softfloat"),
                  ("marble labels (worst)", "lead / main")):
    rows.append(block("box", name, txt, 2.6 if "marble" in name else 7.0,
                      "travel time" if "marble" in name else "visible until dim"))
for s in ("RECORD", "LEDGERS", "VECTORS", "METRICS"):
    rows.append(block("box", f"stamp {s}", s, 2.0, ">=2 s before dim; last stamp worst case"))

bad = [r for r in rows if not r["ok"]]
out = {"rule": "smallest 0.5s multiple >= max(1.5, 0.5 + words/2.5)",
       "totals_words": totals,
       "cut_pct": round(100 * (1 - totals["v5"] / totals["v4"]), 1),
       "blocks": rows, "violations": bad}
(HERE / "audit_text5.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(f"words v4={totals['v4']} v5={totals['v5']} cut={out['cut_pct']}%  blocks={len(rows)} violations={len(bad)}")
for r in rows:
    print(f"{'OK ' if r['ok'] else 'BAD'} {r['scene']:8s} {r['block']:34s} w={r['words']:3d} "
          f"dwell={r['dwell_given_s']:6.2f} min={r['rule_min_s']:.1f}  {r['note']}")
for r in bad:
    print("VIOLATION:", r["scene"], r["block"], r["words"], r["dwell_given_s"], "<", r["rule_min_s"])
