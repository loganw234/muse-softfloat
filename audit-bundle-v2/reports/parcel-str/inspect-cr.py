import pathlib, subprocess
W = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w3-str")
for f in ["tables/implemented.tsv", "src/msf_string.c", "tests/gen_vectors_str.py",
          "src/msf_wide.c", "tests/vectors/pack64.vec"]:
    b = (W / f).read_bytes()
    crlf = b.count(b"\r\n")
    print(f, "size", len(b), "CR", b.count(b"\r"), "CRLF", crlf, "LF", b.count(b"\n"))
b = (W / "tables/implemented.tsv").read_bytes()
lines = b.split(b"\n")
crlines = [i for i, l in enumerate(lines) if l.endswith(b"\r")]
print("implemented CR line indexes (first 10):", crlines[:10], "total", len(crlines))
print("git status:")
print(subprocess.run(["git", "-c", f"safe.directory={W}", "-C", str(W), "status", "--porcelain"],
                     capture_output=True, text=True).stdout)
