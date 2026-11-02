parcel-str: runner to_* calls f64 for f16/f32 (retkind SPECIAL, want argkinds[0])
For: lead
Second runner char bug, measured on 12611 directed vectors: to_* width comes from op->retkind, which is MSF_RK_SPECIAL for char_to rows, so kind_width defaults to 64 and every f16/f32 to_* vector calls the f64 function (5024 fails, all and only msf16/msf32 to_decimal/to_hex; all from_* and all f64 to_* pass). Fix: width from op->argkinds[0] in the to_* branch of process_char_line. Full counts in ledger/parcel-str.md. Smoke otherwise green except the expected planned-only control retirement.

Written: 2026-10-27 08:45:48 -0700
