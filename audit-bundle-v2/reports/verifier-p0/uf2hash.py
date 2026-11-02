"""verifier-p0 UF2/ELF hashes on disk."""
import hashlib
import pathlib

fw = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\muse-softfloat\build\board-fw\fw")
for f in sorted(fw.glob("msf_*.uf2")) + sorted(fw.glob("msf_*.elf")):
    print(f.name, hashlib.sha256(f.read_bytes()).hexdigest())
