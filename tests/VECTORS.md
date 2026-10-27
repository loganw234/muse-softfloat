# Vector format

One case per line, space-separated, `#` starts a comment, blank lines
are ignored. Every counted line carries a provenance tag as its last
field; a vector whose provenance the runner cannot print does not
count toward a gate (SF-0 Section 4.3).

## Public operations

```
<op> <rm> <args...> -> <result> <flags> <provenance>
```

- `<op>` is a generated API name from `docs/COVERAGE.tsv`.
- `<rm>` is `te|tz|tp|tn` for attribute-taking operations, `-`
  otherwise. (`ta` exists only for `internal.pack64` below.)
- `<args...>` are operand bit patterns as hexadecimal integers,
  truncated to the operation's kind width.
- `<result>` is the expected result bits (integers and predicates in
  plain hexadecimal too).
- `<flags>` is the expected flag delta as two hex digits (bits per
  `MSF_FLAG_*`), or `--` for operations that take no flags pointer.

Example:

```
msf16_class - 7e01 -> 1 -- exact-py:f16-exhaustive
```

## The round-and-pack exemplar (internal, P0)

```
internal.pack64 <rm> <sign> <exp2> <sig128> <sticky> -> <result> <flags> <provenance>
```

`sign` and `sticky` are `0|1`, `exp2` is a signed decimal exponent,
`sig128` is up to 32 hex digits. Semantics: `msf_pack_f64` in
`src/msf_roundpack.c`. `<rm>` may also be `ta` (ties-to-away).

## Provenance tags in use

| tag | meaning |
|---|---|
| `exact-py:f16-exhaustive` | every binary16 encoding, expected values from the bit-decode reference in `tests/gen_vectors.py` |
| `exact-py:directed-encodings` | hand-directed exponent/payload edge sets per format, same reference |
| `exact-py:copysign-sample` | seeded sample of binary16 pairs (seed in the generator) |
| `exact-py:pack64-directed` | directed round/pack boundaries, expectations from the independent rational reference in `tests/gen_vectors.py` |
| `exact-py:pack64-sweep` | seeded random round/pack sweep, same reference |
| `berkeley:testfloat_gen-*` | streamed `testfloat_gen` output (from the P0 oracle bring-up onward; the runner inventory prints the oracle hash from the fetch record) |

Berkeley's flag bits are ordered differently from `MSF_FLAG_*`
(inexact=1, underflow=2, overflow=4, infinite/divide-by-zero=8,
invalid=16, measured from its header at P0 bring-up). Berkeley
vectors are translated to our bit order at ingest, and the runner
prints the translation it applied; raw Berkeley flag bytes never
enter a committed vector file.

Generated vector files are produced into the build directory by
`tools/run.sh` (generate-and-replay; nothing budgets storage).
Small directed files under `tests/vectors/` are committed with their
generator named in the header line.
