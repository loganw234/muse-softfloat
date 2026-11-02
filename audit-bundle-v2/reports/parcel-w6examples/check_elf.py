"""Board-less ELF evidence: expected demo strings are in the image."""
ROOT = "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-examples"
elf = open(ROOT + "/build/example-pico/msf_example.elf", "rb").read()
for s in [b"muse-softfloat example (public API, bit patterns in/out)",
          b"augcheck exact-product", b"EXAMPLE PASS",
          b"EXAMPLE-RESULT", b"MSF-EXAMPLE 1 ID",
          b"0.10000000000000001", b"div 1/10 TE"]:
    print(s.decode(), "->", "present" if s in elf else "MISSING")
print("elf bytes:", len(elf))
