import random
import sys

n = int(sys.argv[1])
rng = random.Random(4242)
out = []
while len(out) < n:
    b = rng.getrandbits(32)
    if (b >> 23) & 0xFF == 0xFF:
        continue
    fn = "sin_pi" if len(out) % 2 == 0 else "cos_pi"
    out.append(f"msf32_{fn} {b:x}")
sys.stdout.write("\n".join(out) + "\n")
