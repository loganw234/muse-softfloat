"""Exercise board/host_replay.py pair-line handling with a
fake serial board. The fake replies with the expectations
parsed from the vector file itself (so a correct checker
passes), then with one corrupted tail (must be refused).
Also captures the host runner hash over pair lines."""
import importlib.util
import pathlib
import subprocess
import sys

WS = pathlib.Path(__file__).resolve().parents[3]
REPO = WS / "worktrees" / "w5-aug"
TMP = WS / "scratch" / "parcel-w5aug" / "tmp"
runner = REPO / "build" / "smoke" / "msf_runner.exe"
assert runner.exists(), runner

src = (REPO / "tests" / "vectors" / "aug-f64.vec").read_text().splitlines()
sample = [l for l in src if l and not l.startswith("#")][:24]
sample += [l for l in src if "mul-inexact" not in l and "7ff0" in l][:0]
vec = TMP / "host-replay-sample.vec"
vec.write_bytes(("\n".join(sample) + "\n").encode())

out = subprocess.run([str(runner), "hash", str(vec).replace("\\", "/")],
                     cwd=REPO, capture_output=True, text=True)
print(out.stdout)
assert out.returncode == 0, out.stdout + out.stderr
sha = [l.split()[1] for l in out.stdout.splitlines()
       if l.startswith("whole-run-sha256")][0]
print("host pair-hash sha:", sha)

spec = importlib.util.spec_from_file_location(
    "host_replay", REPO / "board" / "host_replay.py")
hr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hr)

CORRUPT = {"on": False, "done": False}
QUEUE = []


class FakeSerial:
    def __init__(self, port, baud, timeout=0):
        self.timeout = timeout

    def reset_input_buffer(self):
        QUEUE.clear()

    def write(self, data):
        s = data.decode().strip()
        if s == "I":
            QUEUE.append("MSF-HARNESS 1 ID fakefake")
        elif s == "Z":
            QUEUE.append("OK reset")
        elif s == "H":
            QUEUE.append("SHA256 %s COUNT %d" % (sha, len(sample)))
        else:
            tok = s.split()
            arrow = tok.index("->")
            head, tail, flags = tok[arrow + 1], tok[arrow + 2], tok[arrow + 3]
            if CORRUPT["on"] and not CORRUPT["done"]:
                tail = "%016x" % (int(tail, 16) ^ 1)
                CORRUPT["done"] = True
            QUEUE.append("R %s %s %s" % (
                "%016x" % int(head, 16), "%016x" % int(tail, 16), flags))

    def readline(self):
        return (QUEUE.pop(0) + "\n").encode()


hr.serial.Serial = FakeSerial
sys.argv = ["host_replay.py", str(vec), "--port", "FAKE",
            "--expect-sha256", sha]
rc = hr.main()
print("clean replay rc:", rc)
assert rc == 0
CORRUPT.update(on=True, done=False)
rc2 = hr.main()
print("corrupt-tail replay rc:", rc2)
assert rc2 == 1 and CORRUPT["done"]
print("HOST REPLAY PAIR TEST PASS")
