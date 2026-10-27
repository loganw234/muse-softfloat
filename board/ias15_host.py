#!/usr/bin/env python3
"""Host capture for the IAS15 / AEABI-selftest firmwares (lead-run).

Discovers the Pico USB CDC port by VID (or --port), optionally sends
one command line, and streams board lines to the console until
--until MARKER appears (default IAS15-DONE). IAS15FH1 hash-shaped
rows are also written verbatim to --hashes FILE, which is exactly
the input shape of scratch/ias15/work/compare_hashes.py - the lead
compares that file against the desktop reference hashes unchanged.

Timeouts are inactivity-based: a 2000-step board run streams one
line per step at kevery=1 but a timed "T" run prints only per
1000-step block, so the default idle limit is generous (600 s).

Examples (from the repo root, after flashing under the board lock):
  board/ias15_host.py --cmd "R 2000 1" --hashes board_hashes.txt
  board/ias15_host.py --until AEABI-RESULT        # selftest firmware
  board/ias15_host.py --cmd "T 2000"              # step-rate blocks
Exit 0 iff the marker line was seen and contains no FAIL.
"""
import argparse
import re
import sys
import time

import serial
import serial.tools.list_ports

PICO_VID = 0x2E8A
HASH_ROW = re.compile(
    r"^\d+ [0-9a-f]{64} [0-9a-f]{64} [0-9a-f]{16} [0-9a-f]{16} [0-9a-f]{16}$")


def find_port():
    for p in serial.tools.list_ports.comports():
        if p.vid == PICO_VID:
            return p.device
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port")
    ap.add_argument("--cmd", help="one command line to send (e.g. 'R 2000 1')")
    ap.add_argument("--until", default="IAS15-DONE",
                    help="stop when a line contains this marker")
    ap.add_argument("--hashes", help="write IAS15FH1 hash rows to this file")
    ap.add_argument("--idle-timeout", type=float, default=600.0,
                    help="seconds without any board line before failing")
    ap.add_argument("--port-timeout", type=float, default=30.0,
                    help="seconds to wait for the CDC port to enumerate")
    args = ap.parse_args()

    port = args.port
    deadline = time.time() + args.port_timeout
    while not port and time.time() < deadline:
        port = find_port()
        if not port:
            time.sleep(0.5)
    if not port:
        print("board: no Pico CDC port (VID 2e8a) enumerated")
        return 2
    print("board port: %s" % port)
    ser = serial.Serial(port, 115200, timeout=1.0)
    time.sleep(0.3)
    if args.cmd:
        # Re-request the banner first: confirms the right firmware
        # and re-syncs after any boot-time output the open raced.
        ser.write(b"I\n")
        time.sleep(0.2)
        ser.write((args.cmd.strip() + "\n").encode())
        print("board cmd: %s" % args.cmd.strip())

    rows = []
    last_line_at = time.time()
    while True:
        raw = ser.readline()
        if raw:
            last_line_at = time.time()
            s = raw.decode("utf-8", "replace").strip()
            if not s:
                continue
            print(s)
            if HASH_ROW.match(s):
                rows.append(s)
            if s.startswith("# END"):
                rows.append(s)
            if args.until in s:
                break
            if s.startswith("E ") or s.startswith("MSF-TRAP"):
                print("board: error line from firmware")
                return 1
        elif time.time() - last_line_at > args.idle_timeout:
            print("board: no line within idle timeout %ss" % args.idle_timeout)
            return 1

    if args.hashes:
        with open(args.hashes, "w", encoding="utf-8", newline="\n") as f:
            f.write("# IAS15FH1 from board via ias15_host.py\n")
            for r in rows:
                f.write(r + "\n")
        print("wrote %d hash rows to %s"
              % (sum(1 for r in rows if HASH_ROW.match(r)), args.hashes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
