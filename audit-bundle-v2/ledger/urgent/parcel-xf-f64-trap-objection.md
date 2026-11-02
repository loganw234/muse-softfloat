parcel-xf objection: dest-f64 convert-first traps are vacuous; substitution named in design entry
For: lead
Objection before coding around it: brief asks convert-then-operate traps at least one per arithmetic family per dest. For dest f64 convert-first is exact (f16/f32 widen, f64 identity), so no such trap exists for add/sub/mul/div/sqrt to f64. Design entry in ledger/parcel-xf.md names my substitution (unfused-fma and via-binary32 intermediate traps per f64 family, plus sampled zero-difference proof for convert-first). Source code unaffected; proceeding with src and f32 traps, will reshape only tests if you rule otherwise.

Written: 2026-10-27 07:08:30 -0700
