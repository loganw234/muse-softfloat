import pathlib
S = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\controls")
p = S / "msf_string_mut.c"
src = p.read_bytes()
# Mutant: every public entry truncates (force toward-zero everywhere).
# Insert at the two from-generics and two to-generics.
anchors = [
    b"static uint64_t from_decimal_generic(int fmt, const char *s,\n                                     size_t *consumed, int rm,\n                                     msf_flags_t *flags)\n{",
    b"static uint64_t from_hex_generic(int fmt, const char *s,\n                                 size_t *consumed, int rm,\n                                 msf_flags_t *flags)\n{",
    b"static size_t to_decimal_generic(int fmt, uint64_t bits,\n                                 const msf_decimal_spec_t *spec,\n                                 char *buf, size_t buf_size,\n                                 int rm, msf_flags_t *flags)\n{",
    b"static size_t to_hex_generic(int fmt, uint64_t bits,\n                             const msf_hex_spec_t *spec,\n                             char *buf, size_t buf_size,\n                             int rm, msf_flags_t *flags)\n{",
]
for a in anchors:
    assert src.count(a) == 1, a[:40]
    src = src.replace(a, a + b"\n    rm = MSF_IROUND_TOWARD_ZERO; /* MUTANT: truncating */")
p.write_bytes(src)
print("mutant written, size", len(src))
