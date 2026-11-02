import re
from pathlib import Path
p = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-filmretime\video\segments\gitvisual.py")
s = p.read_text(encoding="utf-8")

def sub(pat, rep, txt):
    out, n = re.subn(pat, rep, txt)
    assert n == 1, (pat, n)
    return out

# popup dwell: +0.5 s on each of 7 popups (rule is a minimum)
s = sub(r"POPUP_DWELL = \[rule_dwell\(w\) for w in POPUP_WORDS\]",
        "POPUP_DWELL = [rule_dwell(w) + 0.5 for w in POPUP_WORDS]  # wave6 dwell +0.5 each", s)
# end timings follow T_BOX (which moves with the new SHIFT + gate extras)
s = sub(r"T_BOX = 90\.5.*", "T_BOX = 79.0 + SHIFT  # wave6: aug gate close + 1.5 (was 90.5)", s)
s = sub(r"T_FADE = 86\.0 \+ SHIFT.*", "T_FADE = T_BOX + 9.5  # wave6 (was 86.0+SHIFT=100.0)", s)
s = sub(r"TOTAL = 88\.0 \+ SHIFT.*", "TOTAL = T_FADE + 2.0  # wave6: 108.0 (was 102.0)", s)
# gate windows: ias/kiss 8->9 s, aug 8->8.5 s; legs keep their wall durations
s = sub(r'\{"id": "ias15", "rank": float\(IAS_RANK\), "t0": 39\.0 \+ SHIFT, "t1": 47\.0 \+ SHIFT,',
        '{"id": "ias15", "rank": float(IAS_RANK), "t0": 39.0 + SHIFT, "t1": 48.0 + SHIFT,', s)
s = sub(r'\{"id": "kissfft", "rank": float\(G1_RANK\), "t0": 52\.0 \+ SHIFT, "t1": 60\.0 \+ SHIFT,',
        '{"id": "kissfft", "rank": float(G1_RANK), "t0": 53.0 + SHIFT, "t1": 62.0 + SHIFT,', s)
s = sub(r'\{"id": "augint", "rank": float\(LAST_RANK\), "t0": 67\.0 \+ SHIFT, "t1": 75\.0 \+ SHIFT,',
        '{"id": "augint", "rank": float(LAST_RANK), "t0": 69.0 + SHIFT, "t1": 77.5 + SHIFT,', s)
s = sub(r"\(47\.0 \+ SHIFT, 52\.0 \+ SHIFT, float\(IAS_RANK\), float\(G1_RANK\)\)",
        "(48.0 + SHIFT, 53.0 + SHIFT, float(IAS_RANK), float(G1_RANK))", s)
s = sub(r"\(60\.0 \+ SHIFT, 67\.0 \+ SHIFT, float\(G1_RANK\), float\(LAST_RANK\)\)",
        "(62.0 + SHIFT, 69.0 + SHIFT, float(G1_RANK), float(LAST_RANK))", s)
# window close follows the (lengthened) gate duration: PASS dwells longer
s = sub(r"close = ss\(\(lt - 7\.2\) / 0\.8\)",
        "close = ss((lt - (gate[\"t1\"] - gate[\"t0\"] - 0.8)) / 0.8)  # wave6: dwell before close", s)
p.write_text(s, encoding="utf-8", newline="")
print("patched gitvisual")
