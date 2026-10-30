import json
rows = [
 dict(wave="wave4", brief="ledger/briefs/verify-sf2.md", by="verifier-sf2",
      at="2026-10-28T05:22:48-07:00",
      text="SF-2 draft Sec.5 '616,754 to 594,666 (-78.4%)' - study says 394,666; 594,666 breaks the cited percentage and delta",
      accepted=True),
 dict(wave="wave4", brief="ledger/briefs/verify-sf2.md", by="verifier-sf2",
      at="2026-10-28T05:22:48-07:00",
      text="SF-2 draft Sec.5 pins P1 at 'R1 (underflow not raised)' - in the study R1 raises and R2 (recommended) does not; Sec.5 contradicts Sec.9",
      accepted=True),
 dict(wave="wave4", brief="ledger/briefs/verify-sf2.md", by="verifier-sf2",
      at="2026-10-28T05:22:48-07:00",
      text="SF-2 draft Sec.2 'pack has no ties-to-away mode yet; internal mode 4 added' - tree already has mode 4 + pack arms; only the public enum and string cases are owed",
      accepted=True),
 dict(wave="wave4", brief="ledger/briefs/verify-sf2.md", by="verifier-sf2",
      at="2026-10-28T05:22:48-07:00",
      text="SF-2 draft Sec.2 'MPFR-RNDA/exact elsewhere' drops the study's RNDNA prohibition, emin fence, and trig/sqrt relabel + Niven stop condition",
      accepted=True),
 dict(wave="wave4", brief="ledger/briefs/verify-sf2.md", by="verifier-sf2",
      at="2026-10-28T05:22:48-07:00",
      text="SF-2 draft Sec.4 '4.6x the exp2 demand' misattributes the programme-wide headroom denominator",
      accepted=True),
 dict(wave="wave5", brief="ledger/briefs/study-tokens-visual.md", by="parcel-w5metrics",
      at="2026-10-29T12:26:07-07:00",
      text="tokens-visual study grand total 1,514,499,184 billed double-counts 38,594,472 input tokens (3 sessions re-added under garbled ids); streamed recount at the study's own tmax equals its tree 1,469,302,586 in / 6,444,124 out",
      accepted=True),
]
out = open("muse-softfloat/docs/metrics/corrections.jsonl", "a")
for r in rows:
    ordered = {k: r[k] for k in ("wave","brief","by","at","text","accepted")}
    out.write(json.dumps(ordered) + "\n")
out.close()
print("rows now", sum(1 for _ in open("muse-softfloat/docs/metrics/corrections.jsonl")))
