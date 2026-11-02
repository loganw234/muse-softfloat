"""Regenerate Gate 2 numbers from muse-softfloat/docs/metrics/usage.jsonl at HEAD.
Definition candidates printed; chosen definition written to gate2_numbers.json.
Labeled row = has non-empty wave AND agent fields (checked against brief's 93 rows).
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "muse-softfloat" / "docs" / "metrics" / "usage.jsonl"
rows = [json.loads(l) for l in SRC.read_text(encoding="utf-8").splitlines() if l.strip()]
print(f"total rows: {len(rows)}")
print("keys union:", sorted({k for r in rows for k in r}))
def sums(sel, label):
    i = sum(int(r.get("input_tokens", 0)) for r in sel)
    o = sum(int(r.get("output_tokens", 0)) for r in sel)
    c = sum(int(r.get("cached_tokens", 0)) for r in sel)
    m = sum(int(r.get("messages", 0)) for r in sel)
    print(f"{label}: n={len(sel)} input={i:,} output={o:,} cached={c:,} billed_in+out={i+o:,} messages={m:,}")
    return i, o, c, m
sums(rows, "ALL")
labeled = [r for r in rows if r.get("wave") and r.get("agent")]
i, o, c, m = sums(labeled, "LABELED(wave+agent)")
print("unlabeled agents:", sorted({str(r.get('agent')) for r in rows if not (r.get('wave') and r.get('agent'))}))
print("waves:", sorted({str(r.get('wave')) for r in rows}))
sums([r for r in rows if r.get("source") == "log"], "source=log")
# owner estimate carried from tokens study (frozen, chars/4 over owner prompts)
tok = json.loads((ROOT / "scratch/study-tokens-visual/data/tokens.json").read_text(encoding="utf-8"))
owner = tok["owner"]
print("owner study:", owner["msgs"], owner["chars"], owner["est_tokens"], owner["band"], owner["span"])
print("stale v1 headline:", tok.get("headline"))
billed = i + o
ratio = billed / owner["est_tokens"]
share = 100.0 * owner["est_tokens"] / billed
out = {
    "source": "muse-softfloat/docs/metrics/usage.jsonl at HEAD a73e97d",
    "definition": "LABELED rows only (wave+agent present); project billed = input_tokens + output_tokens; cached_tokens are inside input_tokens (not added again)",
    "labeled_rows": len(labeled), "total_rows": len(rows),
    "input_tokens": i, "output_tokens": o, "cached_tokens_inside_input": c,
    "project_billed_in_plus_out": billed, "messages": m,
    "owner_est_tokens_chars_over_4_frozen_study": owner["est_tokens"],
    "owner_band": owner["band"], "owner_prompts": owner["msgs"], "owner_chars": owner["chars"],
    "ratio_billed_per_owner_token": round(ratio), "human_share_pct": share,
}
( Path(__file__).parent / "gate2_numbers.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
