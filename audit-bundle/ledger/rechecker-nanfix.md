
## 2026-10-26 20:39:46 -0700 - READY on nanfix recheck of 4cdb912

READY on nanfix recheck of 4cdb912 (parent de2d48c): (a) 0, (b) 0, 3 notes, full report in scratch/rechecker-nanfix/report.md.

Measured: diff de2d48c..4cdb912 is exactly the claimed fix and nothing else (src/msf_decode.h 3+/2-); old branch provably unreachable (quiet_bit inside frac_mask on all three widths); NaN probe 236/236 agree with own SF-0 2.5 field-arithmetic reference on fixed code across all 9 format pairs, truncation boundary, widening, signaling, negative, delivery priority and FMA split; parent header fails 19/236, all 19 negative-sign truncate-to-zero (0xfe00/0xffc00000 vs 0x7e00/0x7fc00000), zero failures outside that class; tools/run.sh smoke 29982/29982 PASS in 8s with 9/9 controls refused; no callers of either helper anywhere outside msf_decode.h; tree clean, no cft names.
Believed: parent smoke count 29982/29982 inherited from the verifier-w1prep report (not re-run; count matches at target); truncate-to-zero reachable only via signaling inputs by shift-domain reading (quiet bit always survives narrowing), so the defect class is exactly negative sNaN with tiny narrowing payloads.
For: lead (nanfix push gate).
