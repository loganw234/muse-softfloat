"""build.py - regenerate every generated site artifact from the repo.

Steps: build_data.py (data.json / ops.json / vectors-sample.json),
compile src/*.c + site/glue.c to site/msf.wasm (freestanding wasm32,
src/ unmodified), then replay the bundled sample through the WASM
build under Node and write site/replay-log.txt. Fails loudly if any
step fails; a nonzero replay mismatch count fails the build.

Toolchain: a clang that targets wasm32-freestanding. Developed with
`zig cc` (Zig 0.17.0, scratch-only; URL+sha256 in
ledger/parcel-w5site.md). Point --cc or $MSF_CC at the compiler
command, e.g. --cc "zig cc" or --cc clang. Node is required for the
replay step (--skip-replay to omit).
"""
import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = Path(__file__).resolve().parent
SRC = ["msf16.c", "msf32.c", "msf64.c", "msf_alg.c", "msf_aug.c",
       "msf_flags.c", "msf_math.c", "msf_roundpack.c", "msf_string.c",
       "msf_wide.c"]
EXPORTS = ["msf_op_count", "msf_run", "msf_result_lo", "msf_result_hi",
           "msf_result_flags", "msf_result_ok"]


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    print("+ " + " ".join(cmd), flush=True)
    return subprocess.run(cmd, **kw)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cc", default=os.environ.get("MSF_CC", ""))
    ap.add_argument("--skip-replay", action="store_true")
    args = ap.parse_args()
    if not args.cc:
        print("error: no compiler. Pass --cc \"zig cc\" (or set MSF_CC).",
              file=sys.stderr)
        return 2
    cc = shlex.split(args.cc, posix=False)

    r = run([sys.executable, str(SITE / "build_data.py")])
    if r.returncode != 0:
        return r.returncode

    cmd = cc + ["-target", "wasm32-freestanding", "-O2", "-nostdlib",
                "-Wl,--no-entry", "-Wl,-z,stack-size=1048576"]
    cmd += [f"-Wl,--export={e}" for e in EXPORTS]
    cmd += [str(ROOT / "src" / s) for s in SRC]
    cmd += [str(SITE / "glue.c"), "-o", str(SITE / "msf.wasm")]
    r = run(cmd)
    if r.returncode != 0:
        return r.returncode
    size = (SITE / "msf.wasm").stat().st_size
    print(f"msf.wasm: {size} bytes")

    if not args.skip_replay:
        r = run(["node", str(SITE / "replay.mjs"), str(SITE)],
                capture_output=True, text=True)
        log = r.stdout + r.stderr
        (SITE / "replay-log.txt").write_text(log, encoding="utf-8",
                                             newline="\n")
        print(log, end="")
        if r.returncode != 0:
            print("error: WASM replay failed (see replay-log.txt)",
                  file=sys.stderr)
            return r.returncode
    print("build ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
