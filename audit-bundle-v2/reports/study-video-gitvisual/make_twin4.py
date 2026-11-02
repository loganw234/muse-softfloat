"""1080p downscale twin of gitvisual4.mp4 (secondary; master is 1440p)."""
import subprocess
from pathlib import Path
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
src, dst = HERE / "gitvisual4.mp4", HERE / "gitvisual4-1080.mp4"
cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
       "-i", str(src), "-vf", "scale=1920:1080:flags=lanczos", "-an",
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
       "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dst)]
print(subprocess.run(cmd).returncode, dst, dst.stat().st_size if dst.exists() else 0)
