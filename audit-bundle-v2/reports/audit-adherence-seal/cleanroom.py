"""Clean-room scan of tracked files at HEAD: audio, third-party source,
unexpected blobs. Skips anything with 'cft' in the name (fence: never
open/search/list it -- excluded by name only, not inspected).
Run: MSF_PYTHON cleanroom.py
"""
import subprocess, os

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "muse-softfloat")

def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                          capture_output=True, text=True).stdout

files = [l for l in git("ls-files").split("\n") if l.strip()]
print(f"tracked files: {len(files)}")
fenced = [f for f in files if "cft" in f]
print(f"fenced (cft in name, uninspected): {len(fenced)}")
files = [f for f in files if "cft" not in f]

import collections
exts = collections.Counter(os.path.splitext(f)[1].lower() for f in files)
print("by extension:", dict(exts))
audio = [f for f in files if os.path.splitext(f)[1].lower() in
         (".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".mid", ".midi")]
print(f"audio files tracked: {audio}")

third = [f for f in files if any(k in f.lower() for k in
         ("berkeley", "testfloat", "softfloat-3", "mpfr", "gmp", "kissfft",
          "fftw", "riff", "epidemic", "sunflower"))]
print(f"third-party/license-sensitive names tracked: {len(third)}")
for f in third[:40]:
    print(f"  {f}")

big = []
for f in files:
    p = os.path.join(REPO, f)
    try:
        big.append((os.path.getsize(p), f))
    except OSError:
        pass
big.sort(reverse=True)
print("largest 12:")
for s, f in big[:12]:
    print(f"  {s:>10} {f}")
