# Demo site

The showcase page for muse-softfloat, published at
<https://loganw234.github.io/muse-softfloat/> once GitHub Pages is
enabled (Settings → Pages → Source: GitHub Actions — a one-time
owner action; `.github/workflows/pages.yml` then uploads this
directory as the Pages artifact on every push to `main` that
touches it).

Plain HTML/CSS/JS. No framework, no build-time JS dependencies, and
no external requests at runtime: everything the page loads lives in
this directory.

## What is live and what is recorded

The centrepiece runs the actual library: `msf.wasm` is the
repository's own `src/*.c` (compiled unmodified, freestanding
wasm32) plus `glue.c`, which drives the same generated dispatch
table (`tests/msf_dispatch.h`) the host test runner uses. 810 of
828 instantiations are runnable in the page; the 12 character
conversions and 6 flag-management operations are not hex-drivable
and are omitted (they stay host-gated like everything else).

If WebAssembly cannot load in a visitor's browser, free entry is
disabled and "deal me a committed vector" shows recorded results
from `tests/vectors/`, labelled as recorded. The page never
implies live computation it is not doing.

## Files

| file | what |
|---|---|
| `index.html`, `style.css`, `app.js` | the page (hand-written) |
| `glue.c` | the only site-owned C: WASM exports over the dispatch table |
| `msf.wasm` | generated: library + glue, freestanding wasm32 |
| `data.json` | generated: counts from `docs/COVERAGE.tsv`, `docs/metrics/plants.jsonl`, `tests/vectors/` |
| `ops.json` | generated: op table parsed from `tests/msf_dispatch.h`, joined with `docs/COVERAGE.tsv` |
| `vectors-sample.json` | generated: 1,596-line stratified sample of committed vectors (first + middle line per op) |
| `replay-log.txt` | generated: Node replay of the sample through `msf.wasm` (0 mismatches required) |
| `build_data.py` | regenerates the three JSON files from the repo |
| `replay.mjs` | the Node replay proof |
| `build.py` | all of the above, end to end |

Every number the page displays comes from `data.json` (regenerated
from the named sources) or is a recorded fact quoted from
`docs/RECORD.md` with its context. Timing figures appear only as
recorded facts with units. There are no performance claims.

## Rebuild

Needs a wasm32-freestanding clang (developed with `zig cc` from
Zig 0.17.0, kept in scratch; URL + SHA-256 recorded in the parcel
ledger) and Node for the replay proof:

```
python site/build.py --cc "zig cc"
```

`--cc clang` works with any clang that targets
`wasm32-freestanding`. Add `--skip-replay` to omit the Node proof
(not recommended — the committed `msf.wasm` should always carry a
fresh 0-mismatch `replay-log.txt` beside it).

## View locally

Serve this directory statically (the page uses `fetch`, so
`file://` will not load its data):

```
python -m http.server 8000 --directory site
```

then open <http://127.0.0.1:8000/>.
