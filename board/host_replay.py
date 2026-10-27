#!/usr/bin/env python3
"""Host side of the board harness (SF-0 Section 6 item 7).

Discovers the Pico's USB CDC port by VID/PID (or takes --port),
replays a vector file line by line, checks every result against the
file's expectation locally, then compares the board's whole-run
SHA-256 with the digest the host runner computed for the same file
(passed via --expect-sha256). Prints the board unique ID from the
harness banner. Any mismatch exits nonzero with the line named.

    host_replay.py VECTORS [--port COMx] [--expect-sha256 HEX]
"""
import argparse
import sys
import time

import serial
import serial.tools.list_ports

PICO_VID = 0x2E8A


def find_port():
    for p in serial.tools.list_ports.comports():
        if p.vid == PICO_VID:
            return p.device
    return None


def read_line(ser, timeout=10.0):
    ser.timeout = timeout
    line = ser.readline()
    if not line:
        raise SystemExit("board: timeout waiting for a line")
    return line.decode("utf-8", "replace").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vectors")
    ap.add_argument("--port")
    ap.add_argument("--expect-sha256")
    ap.add_argument("--banner-only", action="store_true",
                    help="read the banner (ID) and stop")
    args = ap.parse_args()

    port = args.port
    deadline = time.time() + 30
    while not port and time.time() < deadline:
        port = find_port()
        if not port:
            time.sleep(0.5)
    if not port:
        print("board: no Pico CDC port (VID 2e8a) enumerated within 30s")
        print("ports seen:", [(p.device, hex(p.vid or 0), p.description)
                              for p in serial.tools.list_ports.comports()])
        return 2
    print("board port: %s" % port)
    ser = serial.Serial(port, 115200, timeout=5)
    time.sleep(0.3)
    ser.reset_input_buffer()

    # ask for the ID line on demand (a boot banner can race the host
    # opening the port), then reset the run state
    ser.write(b"I\n")
    banner = read_line(ser)
    print("board: %s" % banner)
    if not banner.startswith("MSF-HARNESS"):
        print("board: no harness banner (wrong firmware?)")
        return 1
    if args.banner_only:
        return 0
    ser.write(b"Z\n")
    if read_line(ser) != "OK reset":
        print("board: reset not acknowledged")
        return 1

    lines = []
    for raw in open(args.vectors, encoding="utf-8"):
        s = raw.strip()
        if s and not s.startswith("#"):
            lines.append(s)
    print("replaying %d vectors from %s" % (len(lines), args.vectors))
    bad = 0
    for i, s in enumerate(lines, 1):
        ser.write((s + "\n").encode())
        reply = read_line(ser)
        tok = s.split()
        arrow = tok.index("->")
        expect = int(tok[arrow + 1], 16)
        if not reply.startswith("R "):
            print("line %d: board replied %r to %s" % (i, reply, s))
            bad += 1
            continue
        got = int(reply.split()[1], 16)
        width = 64 if tok[0].startswith("msf64") or tok[0].startswith("internal") else (
            16 if tok[0].startswith("msf16") else 32)
        if (got & ((1 << width) - 1)) != (expect & ((1 << width) - 1)):
            print("line %d: board %016x != expected %016x | %s" % (i, got, expect, s))
            bad += 1
    ser.write(b"H\n")
    final = read_line(ser)
    print("board: %s" % final)
    if bad:
        print("board replay: %d mismatches" % bad)
        return 1
    if args.expect_sha256:
        got_sha = final.split()[1] if final.startswith("SHA256") else ""
        if got_sha.lower() != args.expect_sha256.lower():
            print("board replay: whole-run hash mismatch\n  board %s\n  host  %s"
                  % (got_sha, args.expect_sha256))
            return 1
        print("board replay: whole-run hash matches host")
    print("board replay: PASS (%d vectors)" % len(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
