#!/usr/bin/env python3
"""Host capture for the KissFFT Fork B firmware (lead-run).

Discovers the Pico USB CDC port by VID (or --port / MSF_BOARD_PORT),
streams board lines until KISSFFT-DONE, and compares the board's
KF hash rows against --expect FILE (the host proof's KF rows,
scratch/parcel-w4kissfft/out/hashes-main.txt shape). Exit 0 iff
every expected KF row appears verbatim from the board and the
done marker was seen.

The firmware runs all configurations at boot; if the open races
that output, an "R" command re-runs them (sent on --rerun).

Example (from the repo root, after flashing under the board lock):
  board/kissfft_host.py --expect hashes-main.txt --rerun
"""
import argparse
import os
import re
import sys
import time

import serial
import serial.tools.list_ports

PICO_VID = 0x2E8A
KF_ROW = re.compile(r"^KF \d+ (complex|real) (fwd|inv) [0-9a-f]{64}$")


def find_port():
    for p in serial.tools.list_ports.comports():
        if p.vid == PICO_VID:
            return p.device
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default=os.environ.get("MSF_BOARD_PORT"))
    ap.add_argument("--expect", required=True,
                    help="file with expected KF rows (host proof output)")
    ap.add_argument("--rerun", action="store_true",
                    help="send R to re-run the configurations")
    ap.add_argument("--idle-timeout", type=float, default=600.0)
    ap.add_argument("--port-timeout", type=float, default=30.0)
    args = ap.parse_args()

    expect = []
    with open(args.expect, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if KF_ROW.match(line):
                expect.append(line)
    if not expect:
        print("kissfft_host: no KF rows in %s" % args.expect)
        return 2
    print("expecting %d KF rows from %s" % (len(expect), args.expect))

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
    if args.rerun:
        ser.write(b"R\n")
        print("board cmd: R")

    got = []
    last_line_at = time.time()
    while True:
        raw = ser.readline()
        if raw:
            last_line_at = time.time()
            s = raw.decode("utf-8", "replace").strip()
            if not s:
                continue
            print(s)
            if KF_ROW.match(s):
                got.append(s)
            if s.startswith("E ") or s.startswith("MSF-TRAP"):
                print("board: error line from firmware")
                return 1
            if "KISSFFT-DONE" in s:
                break
        elif time.time() - last_line_at > args.idle_timeout:
            print("board: no line within idle timeout %ss" % args.idle_timeout)
            return 1

    missing = [r for r in expect if r not in got]
    extra = [r for r in got if r not in expect]
    if missing or extra or len(got) != len(expect):
        for r in missing:
            print("MISSING/MISMATCH expected: %s" % r)
        for r in extra:
            print("UNEXPECTED from board:  %s" % r)
        print("kissfft_host: FAIL got=%d expect=%d" % (len(got), len(expect)))
        return 1
    print("kissfft_host: PASS all %d KF rows bit-identical" % len(expect))
    return 0


if __name__ == "__main__":
    sys.exit(main())
