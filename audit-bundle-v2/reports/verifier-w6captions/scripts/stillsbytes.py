"""Byte-compare 6 fresh grabs vs committed stills (verifier-owned)."""
import subprocess
from pathlib import Path
import imageio_ffmpeg

BASE = Path("C:/Users/logan/source/repos/Muse-Softfloat")
MP4 = BASE / "worktrees/verify6-captions/video/out/assembly_v6.mp4"
ST = BASE / "worktrees/verify6-captions/video/out/stills_v6"
OUT = BASE / "scratch/verifier-w6captions/refetch"
OUT.mkdir(parents=True, exist_ok=True)
exe = imageio_ffmpeg.get_ffmpeg_exe()
PICKS = ["01_t002.90_intro-msg.png", "07_t037.26_why-spec.png",
         "13_t071.13_git-popup-parcels.png", "22_t123.39_git-gate-ias15.png",
         "25_t152.42_git-gate-augint.png", "30_t177.82_outro-stats.png"]
for f in PICKS:
    t = float(f.split("_t")[1].split("_")[0])
    dst = OUT / f
    subprocess.run([exe, "-y", "-hide_banner", "-loglevel", "error",
                    "-ss", f"{t:.3f}", "-i", str(MP4),
                    "-frames:v", "1", str(dst)], check=True)
    a = (ST / f).read_bytes()
    b = dst.read_bytes()
    print(f"{f} t={t:.2f} committed={len(a)} fresh={len(b)} "
          f"{'IDENTICAL' if a == b else 'DIFFER'}")
