# Board harness (P0)

Firmware and host scripts for RP2040 on-silicon evidence. Everything
here runs lead-only under `<ledger>/board.lock` via
`tools/run.sh board|bench` (docs/BOARD.md owns the protocol).

## Targets

| target | what |
|---|---|
| `msf_board_harness` | USB CDC vector replay with whole-run SHA-256 (`harness_main.c`) |
| `msf_hello` | interposition hello: `--wrap=copysignf/copysign` onto `compat/msf_wrap.c`, per-core/IRQ wrapper-state self-test (`hello_main.c`) |
| `msf_bench` | bench skeleton: placement/clock-labelled cycle/size reporting, no claims (`bench_main.c`) |

## LED activity indicator

`msf_led.h` blinks the onboard LED at ~2 Hz while a firmware is
doing work — vector replay, IAS15 runs, KissFFT configurations,
interval rows, bench reports — and turns it off when the firmware
is idle waiting for input, so a row of boards shows which are
running. Both bench wirings are driven from the same image (board
type is not runtime-detectable): the Pico's plain LED on
`PICO_DEFAULT_LED_PIN` (GP25) by GPIO, and the RP2040-Zero clones'
WS2812 RGB LED on GP16 by a minimal PIO program (frames sent only
on blink-phase changes; harmless on a Pico, where GP16 is an
unconnected header pin). No effect on any computed value or hash,
and calls sit outside timed regions next to the printing those
timings already exclude.

## Replay protocol

Text lines over USB CDC at any baud (CDC ignores it). On boot the
harness prints `MSF-HARNESS 1 ID <unique-id-hex> BUILD <date> <time>`;
`I` re-prints the ID line on demand (a boot banner can race the host
opening the port).
Commands: `Z` resets the run hash/count and replies `OK reset`;
`H` replies `SHA256 <digest> COUNT <n>`. Any other line is a vector
line in the `tests/VECTORS.md` format: the board executes the named
operation (expectations in the line are ignored), folds the canonical
result line into the hash — byte-identical to `msf_runner hash` on
the host — and replies `R <result-hex> <flags-hex>` or `E <reason>`
(`unknown`, `planned`, `malformed`, `noshape`). `board/host_replay.py`
checks each result against the file and the final digest against the
host's.

## Flash and re-entry

`common.sh` flashes with `picotool load -f -x`: `-f` reboots a
running device with a USB serial connection so the load can proceed
(measured necessary here — a plain `picotool reboot -u` was not
answered by running firmware). If the load still fails, the board
needs hands — hold BOOTSEL while plugging in — and the budget says
so by name.
