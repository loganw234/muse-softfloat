import re, subprocess
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
for name in ("assembly_v6_musicA_stretch.mp4", "assembly_v6_musicB_native124.mp4"):
    p = subprocess.run([FF, "-i", f"scratch/lead/music/{name}",
                        "-map", "0:a", "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True)
    mean = re.search(r"mean_volume: ([-\d.]+) dB", p.stderr)
    mx = re.search(r"max_volume: ([-\d.]+) dB", p.stderr)
    print(f"{name}: mean {mean.group(1)} dB, max {mx.group(1)} dB")
# spot-check B's fade: last-3s mean should be well below mid-film mean
for label, ss, t in (("B mid 90-100s", "90", "10"), ("B tail 176-179s", "176", "3")):
    p = subprocess.run([FF, "-ss", ss, "-t", t, "-i",
                        "scratch/lead/music/assembly_v6_musicB_native124.mp4",
                        "-map", "0:a", "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True)
    mean = re.search(r"mean_volume: ([-\d.]+) dB", p.stderr)
    print(f"{label}: mean {mean.group(1)} dB")
