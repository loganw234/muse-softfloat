import subprocess
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
# gitvisual segment starts at 62.90s scaled; parcels card native 8.5s
t = 62.90 + 8.5 * 120.0 / 124.0
subprocess.run([FF, "-y", "-ss", f"{t:.2f}", "-i",
                "muse-softfloat/video/out/assembly_v6.mp4",
                "-frames:v", "1", "scratch/lead/popup_stills/assembly_parcels.png"],
               capture_output=True)
print(f"grabbed at {t:.2f}s")
