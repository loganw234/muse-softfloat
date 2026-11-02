import pathlib
src = pathlib.Path("ledger/briefs/w1-f64.md").read_text(encoding="utf-8")
out = src.replace("parcel-f64 (binary64 format parcel", "parcel-f32 (binary32 format parcel")
out = out.replace("Every wave-1 binary64 instantiation", "Every wave-1 binary32 instantiation")
out = out.replace("name starts\n`msf64_`", "name starts\n`msf32_`")
out = out.replace("branch `w1-f64`", "branch `w1-f32`")
out = out.replace("worktrees/w1-f64", "worktrees/w1-f32")
out = out.replace("ledger/parcel-f64.md", "ledger/parcel-f32.md")
out = out.replace("ledger/urgent/parcel-f64-test.md", "ledger/urgent/parcel-f32-test.md")
out = out.replace("scratch/parcel-f64/", "scratch/parcel-f32/")
out = out.replace("scratch/parcel-f64/report.md", "scratch/parcel-f32/report.md")
out = out.replace("ONE\nrounding via `msf_pack_f64` (cross-format dest: `msf_pack_generic`\nis for your dest only — you own dest=64; conversions to f32 are the\nother parcel's)",
                  "ONE\nrounding via `msf_pack_f32` (cross-format dest: `msf_pack_generic`\nis for your dest only — you own dest=32; conversions to f64 are the\nother parcel's)")
out = out.replace("`msf_u128_mul_u64_u64` (53×53 fits)", "`msf_u128_mul_u64_u64` (24×24 fits; 64-bit sources widen exactly)")
out = out.replace("exact 106-bit product", "exact product (48 bits for f32×f32; wider when a source is f64)")
out = out.replace("- logB: normalized exponent (subnormals count their leading zeros),\n  delivered as binary64;",
                  "- logB: normalized exponent (subnormals count their leading zeros),\n  delivered as binary64 (logBFormat) even from your f32 source;")
out = out.replace("- convertFormat (from f32, from f64):", "- convertFormat (from f32, from f64; both land in your dest):")
out = out.replace("**Files you own:** `src/msf64.c`; `tests/gen_vectors_f64.py` (new);\n`tests/vectors/*f64*.vec`",
                  "**Files you own:** `src/msf32.c`; `tests/gen_vectors_f32.py` (new);\n`tests/vectors/*f32*.vec`")
out = out.replace("for f64_add/sub/mul/div/sqrt/rem/roundToInt and both convert\n   directions and f64_to_i32/i64/ui32/ui64 + i32/i64/ui32/ui64_to_f64:",
                  "for f32_add/sub/mul/div/sqrt/rem/roundToInt, f64_to_f32 +\n   f32_to_f32 paths Berkeley covers, and f32_to_i32/i64/ui32/ui64 + i32/i64/ui32/ui64_to_f32:")
out = out.replace("f64_mulAdd level 1", "f32_mulAdd level 1")
out = out.replace("`tests/gen_vectors_f64.py`", "`tests/gen_vectors_f32.py`")
pathlib.Path("ledger/briefs/w1-f32.md").write_text(out, encoding="utf-8")
print("written", len(out))
for i, ln in enumerate(out.splitlines(), 1):
    if "f64" in ln:
        print(i, ln.strip()[:100])
