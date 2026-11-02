import pathlib
import subprocess
import sys

repo = pathlib.Path(sys.argv[1])
base = subprocess.run(["git", "show", "HEAD:tools/run.sh"], cwd=repo,
                      capture_output=True, check=True).stdout.decode()
old = 'SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"'
new = 'SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"'
assert base.count(old) == 1
(repo / "tools" / "run.sh").write_bytes(base.replace(old, new).encode())
print("run.sh reduced to kernel-stage (SRC only)")
