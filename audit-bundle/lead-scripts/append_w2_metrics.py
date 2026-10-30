# Append Wave 2 plants/corrections/escalations rows from the staged files.
import pathlib

DST = pathlib.Path("muse-softfloat/docs/metrics")
plants = pathlib.Path("scratch/lead/plants-w2.txt").read_text()
with (DST / "plants.jsonl").open("a") as f:
    f.write(plants if plants.endswith("\n") else plants + "\n")
mode = None
for line in pathlib.Path("scratch/lead/corr-esc-w2.txt").read_text().splitlines():
    if line == "CORRECTIONS":
        mode = "corrections.jsonl"
    elif line == "ESCALATIONS":
        mode = "escalations.jsonl"
    elif line.strip():
        with (DST / mode).open("a") as f:
            f.write(line + "\n")
print("appended")
