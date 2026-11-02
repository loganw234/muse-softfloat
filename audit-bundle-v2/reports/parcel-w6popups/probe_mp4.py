"""Probe (c): gitvisual7.mp4 must be 108.0 s, 2560x1440@30, silent.

Two independent routes: ffmpeg header text, and decoded frame count
plus first-frame size via imageio-ffmpeg.
"""
import subprocess

MP4 = "video/segments/gitvisual7.mp4"
FF = ("C:/Users/logan/source/repos/Muse-Softfloat/.venv/Lib/site-packages"
      "/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe")

p = subprocess.run([FF, "-hide_banner", "-i", MP4],
                   capture_output=True, text=True)
info = p.stderr
print(info)
ok_dur = "Duration: 00:01:48.00" in info
ok_video = "2560x1440" in info and "30 fps" in info
ok_silent = "Audio:" not in info
print("duration_108.0:", ok_dur)
print("video_2560x1440_30fps:", ok_video)
print("silent:", ok_silent)

import imageio.v3 as iio

meta = iio.immeta(MP4)
print("meta:", {k: meta[k] for k in ("shape", "fps", "duration", "nframes")
                if k in meta})
n = 0
for _ in iio.imiter(MP4):
    n += 1
print("decoded frames:", n, "expect 3240:", n == 3240)
frame0 = iio.imread(MP4, index=0)
print("frame0 shape:", frame0.shape)
assert ok_dur and ok_video and ok_silent and n == 3240
assert tuple(frame0.shape[:2]) == (1440, 2560)
print("MP4 PROBE: PASS")
