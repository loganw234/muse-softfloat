import re, subprocess
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
mp3 = "ES_Sunflower Dance - Helmut Schenker.mp3"
p = subprocess.run([FF, "-i", mp3], capture_output=True, text=True)
print(p.stderr)
m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", p.stderr)
dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
film = 179.03
print(f"track {dur:.2f}s; film {film}s; over by {dur - film:.2f}s; "
      f"atempo factor {dur / film:.6f} (+{(dur / film - 1) * 100:.2f}% tempo)")
