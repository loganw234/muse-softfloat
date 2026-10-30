import pathlib
p = pathlib.Path("ledger/briefs/w1-f32.md")
t = p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
t = t.replace("for f32_add/sub/mul/div/sqrt/rem/roundToInt, f64_to_f32 +\n   f32_to_f32 paths Berkeley covers, and f32_to_i32/i64/ui32/ui64 + i32/i64/ui32/ui64_to_f32:",
              "for f32_add/sub/mul/div/sqrt/rem/roundToInt, f64_to_f32, and\n   f32_to_i32/i64/ui32/ui64 + i32/i64/ui32/ui64_to_f32:")
t = t.replace("cross-format instantiations, 8/16-bit and Exact integer",
              "cross-format instantiations (incl. same-format convertFormat,\n   which Berkeley has no generator for), 8/16-bit and Exact integer")
p.write_bytes(t.encode("utf-8"))
print("crlf:", t.count("\r"), "| len", len(t))
