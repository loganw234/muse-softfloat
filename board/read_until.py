#!/usr/bin/env python3
"""Print Pico CDC lines until one contains MARKER (hello/bench)."""
import sys
import time

import serial
import serial.tools.list_ports


def find_port():
    for p in serial.tools.list_ports.comports():
        if p.vid == 0x2E8A:
            return p.device
    return None


def main():
    marker = sys.argv[1]
    port = None
    deadline = time.time() + 30
    while not port and time.time() < deadline:
        port = find_port()
        if not port:
            time.sleep(0.5)
    if not port:
        print("board: no Pico CDC port (VID 2e8a) enumerated within 30s")
        return 2
    print("board port: %s" % port)
    ser = serial.Serial(port, 115200, timeout=10)
    t_end = time.time() + 60
    while time.time() < t_end:
        line = ser.readline()
        if not line:
            continue
        s = line.decode("utf-8", "replace").strip()
        print(s)
        if marker in s:
            return 0 if "FAIL" not in s or "BENCH" in s else 1
    print("board: marker %r not seen within 60s" % marker)
    return 1


if __name__ == "__main__":
    sys.exit(main())
