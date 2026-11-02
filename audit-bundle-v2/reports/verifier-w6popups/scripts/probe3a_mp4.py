"""Probe3a: mp4 metadata (duration/resolution/fps/audio/streams) via bundled ffmpeg."""
import json, subprocess, sys
from pathlib import Path
import imageio_ffmpeg
DUP = Path(sys.argv[1]).resolve()
mp4 = DUP / "video/segments/gitvisual7.mp4"
ff = imageio_ffmpeg.get_ffmpeg_exe()
print("ffmpeg:", ff)
print("mp4 bytes:", mp4.stat().st_size)
p = subprocess.run([ff, "-i", str(mp4)], capture_output=True, text=True)
print(p.stderr[-2500:])
# frame count via ffprobe-less decode count? use reader metadata
import imageio.v2 as imageio
try:
    r = imageio.get_reader(str(mp4), "ffmpeg")
    md = r.get_meta_data()
    print("imageio meta:", json.dumps({k: md[k] for k in
          ("size", "fps", "duration", "nframes", "codec", "audio_codec") if k in md}, indent=1))
    print("full meta keys:", list(md.keys()))
except Exception as e:
    print("reader err:", e)
