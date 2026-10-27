#!/usr/bin/env python3
"""Generate the P0 seam from tables/formats.tsv + tables/operations.tsv.

Outputs (all byte-deterministic; tools/run.sh regenerates into a temp dir
and refuses on any difference - SF-0 Section 6 items 2-3):

  include/muse_softfloat.h   the public API (SF-0 Section 3.3)
  src/msf_formats.h          internal per-format constants
  tests/msf_dispatch.h       runner dispatch over every instantiation
  docs/COVERAGE.tsv          per-instantiation coverage ledger (4.3)

    tools/gen_tables.py [OUTDIR]   (default: repository root)

The expansion rules live here and nowhere else. Authority tokens:
  berkeley                     pinned Berkeley SoftFloat 3e decides
  mpfr-exact                   MPFR / exact-integer generation decides
  project-exact                project-owned exact reference (test code)
  project-exact+berkeley-check project reference decides, Berkeley
                               cross-checks where it covers the family
  auto-arith                   berkeley when all formats agree,
                               else mpfr-exact (cross-format exactness)
  auto-int                     berkeley for 32/64-bit integers (what 3e
                               provides), else mpfr-exact
Wave rule: a wave-1 instantiation touching binary16 is claimed in
wave 2 (SF-0 Section 7). Status is per family in the table.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INTS = ["i8", "u8", "i16", "u16", "i32", "u32", "i64", "u64"]
INT_TYPE = {"i8": "int8_t", "u8": "uint8_t", "i16": "int16_t", "u16": "uint16_t",
            "i32": "int32_t", "u32": "uint32_t", "i64": "int64_t", "u64": "uint64_t"}


def read_tsv(path):
    rows, header = [], None
    for line in path.read_text(encoding="utf-8").split("\n"):
        if not line or line.startswith("#"):
            continue
        cells = line.split("\t")
        if header is None:
            header = cells
        else:
            assert len(cells) == len(header), (path, line)
            rows.append(dict(zip(header, cells)))
    return rows


FORMATS = read_tsv(ROOT / "tables" / "formats.tsv")
FMT = [f["name"] for f in FORMATS]                     # f16 f32 f64
MTYPE = {f["name"]: "msf%s_t" % f["name"][1:] for f in FORMATS}


def suffix(srcs):
    return "".join("_%s" % s for s in srcs)


def wave_of(row, fmts):
    w = int(row["wave"])
    if w == 1 and "f16" in fmts:
        w = 2
    return w


def authority_of(row, fmts, int_tok):
    a = row["authority"]
    if a == "auto-arith":
        return "berkeley" if len(set(fmts)) == 1 else "mpfr-exact"
    if a == "auto-int":
        return "berkeley" if int(int_tok[1:]) >= 32 else "mpfr-exact"
    return a


def expand(row):
    """Yield instantiation dicts for one family row."""
    sig, op = row["sig"], row["op"]
    out = []

    def emit(name, dest, srcs, decl, fmts, int_tok=None, retkind=None, argkinds=None):
        out.append({
            "name": name, "std_name": row["std_name"], "clause": row["clause"],
            "sig": sig, "dest": dest, "sources": ",".join(srcs),
            "rounding": row["rounding"], "flags": row["flags"],
            "wave": wave_of(row, fmts), "status": "planned",
            "authority": authority_of(row, fmts, int_tok or "i32"),
            "vectors": row["vectors"], "comparison": row["comparison"],
            "decl": decl, "retkind": retkind or ("MSF_RK_" + dest.upper()),
            "argkinds": argkinds if argkinds is not None
                        else ["MSF_AK_" + s.upper() for s in srcs],
        })

    rm = ", msf_rounding_t rm" if row["rounding"] == "attr" else ""
    fl = ", msf_flags_t *flags" if row["flags"] == "yes" else ""

    if sig in ("rint_named", "rint_exact", "next", "sign_un", "classify",
               "class_op", "radix_op"):
        ret = {"classify": "int", "class_op": "msf_class_t",
               "radix_op": "int"}.get(sig)
        rk = {"classify": "MSF_RK_BOOL", "class_op": "MSF_RK_CLASS",
              "radix_op": "MSF_RK_INT"}.get(sig)
        for f in FMT:
            r = ret or MTYPE[f]
            emit("msf%s_%s" % (f[1:], op), f if ret is None else
                 ("bool" if sig == "classify" else ("class" if sig == "class_op" else "int")),
                 [f], "%s msf%s_%s(%s a%s%s);" % (r, f[1:], op, MTYPE[f], rm, fl),
                 [f], retkind=rk)
    elif sig in ("remainder", "sign_bin", "totalorder"):
        ret = "int" if sig == "totalorder" else None
        for f in FMT:
            r = ret or MTYPE[f]
            emit("msf%s_%s" % (f[1:], op), "bool" if ret else f, [f, f],
                 "%s msf%s_%s(%s a, %s b%s%s);" % (r, f[1:], op, MTYPE[f], MTYPE[f], rm, fl),
                 [f], retkind="MSF_RK_BOOL" if ret else None)
    elif sig == "scaleb":
        for f in FMT:  # second operand in logBFormat = binary64 (SF-0 2.2)
            emit("msf%s_scale_b" % f[1:], f, [f, "f64"],
                 "%s msf%s_scale_b(%s a, msf64_t n%s%s);" % (MTYPE[f], f[1:], MTYPE[f], rm, fl),
                 [f])
    elif sig == "logb":  # result in logBFormat = binary64 (SF-0 2.2)
        for f in FMT:
            emit("msf%s_log_b" % f[1:], "f64", [f],
                 "msf64_t msf%s_log_b(%s a%s);" % (f[1:], MTYPE[f], fl), [f])
    elif sig == "arith_bin":
        for d in FMT:
            for s1 in FMT:
                for s2 in FMT:
                    nm = "msf%s_%s" % (d[1:], op) if d == s1 == s2 else \
                         "msf%s_%s%s" % (d[1:], op, suffix([s1, s2]))
                    emit(nm, d, [s1, s2],
                         "%s %s(%s a, %s b%s%s);" % (MTYPE[d], nm, MTYPE[s1], MTYPE[s2], rm, fl),
                         [d, s1, s2])
    elif sig == "arith_un":
        for d in FMT:
            for s in FMT:
                nm = "msf%s_%s" % (d[1:], op) if d == s else "msf%s_%s_%s" % (d[1:], op, s)
                emit(nm, d, [s], "%s %s(%s a%s%s);" % (MTYPE[d], nm, MTYPE[s], rm, fl), [d, s])
    elif sig == "fma":
        for d in FMT:
            for s1 in FMT:
                for s2 in FMT:
                    for s3 in FMT:
                        nm = "msf%s_fma" % d[1:] if d == s1 == s2 == s3 else \
                             "msf%s_fma%s" % (d[1:], suffix([s1, s2, s3]))
                        emit(nm, d, [s1, s2, s3],
                             "%s %s(%s a, %s b, %s c%s%s);" %
                             (MTYPE[d], nm, MTYPE[s1], MTYPE[s2], MTYPE[s3], rm, fl),
                             [d, s1, s2, s3])
    elif sig == "from_int":
        for d in FMT:
            for i in INTS:
                nm = "msf%s_from_%s" % (d[1:], i)
                emit(nm, d, [i], "%s %s(%s a%s%s);" % (MTYPE[d], nm, INT_TYPE[i], rm, fl),
                     [d], int_tok=i)
    elif sig == "to_int":
        for f in FMT:
            for i in INTS:
                nm = "msf%s_%s" % (f[1:], op.replace("<int>", i))
                emit(nm, i, [f], "%s %s(%s a%s);" % (INT_TYPE[i], nm, MTYPE[f], fl),
                     [f], int_tok=i, retkind="MSF_RK_" + i.upper())
    elif sig == "conv_fmt":
        for d in FMT:
            for s in FMT:
                nm = "msf%s_from_%s" % (d[1:], s)
                emit(nm, d, [s], "%s %s(%s a%s%s);" % (MTYPE[d], nm, MTYPE[s], rm, fl), [d, s])
    elif sig == "char_from":
        for f in FMT:
            nm = "msf%s_%s" % (f[1:], op)
            emit(nm, f, ["str"],
                 "%s %s(const char *s, size_t *consumed%s%s);" % (MTYPE[f], nm, rm, fl),
                 [f], argkinds=[])
    elif sig in ("char_to_dec", "char_to_hex"):
        spec = "msf_decimal_spec_t" if sig == "char_to_dec" else "msf_hex_spec_t"
        for f in FMT:
            nm = "msf%s_%s" % (f[1:], op)
            emit(nm, "size", [f],
                 "size_t %s(%s a, const %s *spec, char *buf, size_t buf_size%s%s);" %
                 (nm, MTYPE[f], spec, rm, fl), [f], retkind="MSF_RK_SPECIAL")
    elif sig == "compare":
        for s1 in FMT:
            for s2 in FMT:
                nm = "msf%s_%s" % (s1[1:], op) if s1 == s2 else \
                     "msf%s_%s_%s" % (s1[1:], op, s2)
                emit(nm, "bool", [s1, s2],
                     "int %s(%s a, %s b%s);" % (nm, MTYPE[s1], MTYPE[s2], fl),
                     [s1, s2], retkind="MSF_RK_BOOL")
    elif sig == "version_op":
        emit("msf_%s" % op, "bool", [], "int msf_%s(void);" % op, [],
             retkind="MSF_RK_BOOL", argkinds=[])
        for f in FMT:
            emit("msf%s_%s" % (f[1:], op), "bool", [],
                 "int msf%s_%s(void);" % (f[1:], op), [f],
                 retkind="MSF_RK_BOOL", argkinds=[])
    elif sig == "flag_op":
        emit("msf_%s" % op, "state", [], FLAG_DECLS[op], [],
             retkind="MSF_RK_SPECIAL", argkinds=[])
    else:
        raise SystemExit("unknown sig class: %s" % sig)
    return out


FLAG_DECLS = {
    "lower_flags": "void msf_lower_flags(msf_flags_t *state, msf_flags_t group);",
    "raise_flags": "void msf_raise_flags(msf_flags_t *state, msf_flags_t group);",
    "test_flags": "int msf_test_flags(const msf_flags_t *state, msf_flags_t group);",
    "test_saved_flags": "int msf_test_saved_flags(msf_saved_flags_t saved, msf_flags_t group);",
    "restore_flags": "void msf_restore_flags(msf_flags_t *state, msf_saved_flags_t saved, msf_flags_t group);",
    "save_all_flags": "msf_saved_flags_t msf_save_all_flags(const msf_flags_t *state);",
}


REPLAYABLE = {"rint_named", "rint_exact", "next", "remainder", "scaleb",
              "logb", "arith_bin", "arith_un", "fma", "from_int", "to_int",
              "conv_fmt", "sign_un", "sign_bin", "compare", "totalorder",
              "classify", "class_op", "radix_op", "version_op"}


def ctype(tok):
    if tok in MTYPE:
        return MTYPE[tok]
    return INT_TYPE[tok]


def wrapper_for(o):
    """A correctly typed trampoline so the runner calls one shape."""
    if o["status"] != "implemented" or o["sig"] not in REPLAYABLE:
        return None
    srcs = o["sources"].split(",") if o["sources"] else []
    call_args = ["(%s)args[%d]" % (ctype(s), i) for i, s in enumerate(srcs)]
    if o["rounding"] == "attr":
        call_args.append("(msf_rounding_t)rm")
    if o["flags"] == "yes":
        call_args.append("flags")
    expr = "%s(%s)" % (o["name"], ", ".join(call_args))
    if o["dest"] in ("i8", "i16", "i32", "i64"):
        expr = "(uint64_t)(int64_t)(%s)" % expr
    else:
        expr = "(uint64_t)(%s)" % expr
    voids = ""
    if o["rounding"] != "attr":
        voids += " (void)rm;"
    if o["flags"] != "yes":
        voids += " (void)flags;"
    if not srcs:
        voids += " (void)args;"
    return ("static uint64_t msf_call_%s(const uint64_t *args, int rm, msf_flags_t *flags)"
            " {%s return %s; }" % (o["name"], voids, expr))


def instantiate():
    ops = []
    for row in read_tsv(ROOT / "tables" / "operations.tsv"):
        ops.extend(expand(row))
    names = [o["name"] for o in ops]
    assert len(names) == len(set(names)), "duplicate instantiation names"
    impl = {r["name"]: int(r["wave"])
            for r in read_tsv(ROOT / "tables" / "implemented.tsv")}
    assert len(impl) == len(read_tsv(ROOT / "tables" / "implemented.tsv")), \
        "duplicate rows in implemented.tsv"
    known = set(names)
    for name in impl:
        assert name in known, "implemented.tsv names unknown instantiation: %s" % name
    for o in ops:
        if o["name"] in impl:
            assert impl[o["name"]] == o["wave"], \
                "implemented.tsv wave drift: %s" % o["name"]
            o["status"] = "implemented"
    return ops


HEADER_PRELUDE = """/* muse_softfloat.h - Muse-Softfloat public API.
 *
 * GENERATED by tools/gen_tables.py from tables/formats.tsv and
 * tables/operations.tsv. Do not edit: the runner refuses drift.
 *
 * Pure C11 over integer bit containers (docs/studies/SF-0.md Section 3.3).
 * Values are the IEEE 754-2019 binary16/32/64 interchange encodings held
 * in unsigned integers. Rounding is an explicit argument, never process
 * state. Exception flags accumulate by bitwise OR into caller-owned
 * state; a flags pointer is required non-null wherever one is taken
 * (SF-0 Section 2.4). No traps, no allocation, no floating arithmetic
 * in the core. Tininess is detected after rounding (SF-0 Section 2.5);
 * NaN delivery follows the matrix there. <fenv.h> is not emulated; the
 * compatibility layers live outside this header.
 *
 * Naming: msf<dest>_<op> for homogeneous operations; formatOf forms
 * append the source formats (msf32_add_f64_f64, msf64_fma_f32_f32_f64).
 * Comparisons lead with the first source format and append the second
 * when it differs. logB results and scaleB second operands are in
 * logBFormat = binary64 (SF-0 Section 2.2).
 *
 * Integer conversions that signal invalid (NaN, infinite, or
 * out-of-range operand) deliver the saturated result: positive overflow
 * to the largest destination value, negative to the smallest (zero for
 * unsigned), NaN to zero. 754-2019 5.8 leaves that value
 * implementation-defined; this is the project rule.
 *
 * Character output returns the would-be length excluding the NUL and
 * writes nothing when the buffer cannot hold result plus NUL
 * (SF-0 Section 2.6). Character input reports the consumed prefix
 * length through `consumed` (which may be NULL); with no valid prefix
 * it returns positive zero, consumes nothing, and signals nothing.
 * Correct rounding is promised for significant-digit counts 1..H with
 * H = MSF_DECIMAL_H (SF-0 Section 2.6).
 *
 * Each declaration's comment names its clause and claiming wave; a
 * declaration is not a conformance claim until that wave's gate has
 * closed (SF-0 Section 5.3). Implementation status per instantiation
 * lives in docs/COVERAGE.tsv.
 */
#ifndef MUSE_SOFTFLOAT_H
#define MUSE_SOFTFLOAT_H

#include <stddef.h>
#include <stdint.h>

typedef uint16_t msf16_t;
typedef uint32_t msf32_t;
typedef uint64_t msf64_t;

/* Required binary rounding-direction attributes (754-2019 4.3).
 * Ties-to-away exists only in the operation-named forms (SF-0 2.3). */
typedef enum msf_rounding {
    MSF_ROUND_TIES_TO_EVEN = 0,
    MSF_ROUND_TOWARD_ZERO = 1,
    MSF_ROUND_TOWARD_POSITIVE = 2,
    MSF_ROUND_TOWARD_NEGATIVE = 3
} msf_rounding_t;

/* The five Clause 7 exception flags as bits in caller-owned state. */
typedef uint32_t msf_flags_t;
#define MSF_FLAG_INVALID          ((msf_flags_t)0x01u)
#define MSF_FLAG_DIVISION_BY_ZERO ((msf_flags_t)0x02u)
#define MSF_FLAG_OVERFLOW         ((msf_flags_t)0x04u)
#define MSF_FLAG_UNDERFLOW        ((msf_flags_t)0x08u)
#define MSF_FLAG_INEXACT          ((msf_flags_t)0x10u)
#define MSF_FLAGS_ALL             ((msf_flags_t)0x1fu)

/* Opaque saved-flags value (5.7.4): produced by msf_save_all_flags,
 * consumed only by msf_restore_flags / msf_test_saved_flags. */
typedef uint32_t msf_saved_flags_t;

/* The ten classes of 5.7.2, in the order the clause lists them. */
typedef enum msf_class {
    MSF_CLASS_SIGNALING_NAN = 0,
    MSF_CLASS_QUIET_NAN = 1,
    MSF_CLASS_NEGATIVE_INFINITY = 2,
    MSF_CLASS_NEGATIVE_NORMAL = 3,
    MSF_CLASS_NEGATIVE_SUBNORMAL = 4,
    MSF_CLASS_NEGATIVE_ZERO = 5,
    MSF_CLASS_POSITIVE_ZERO = 6,
    MSF_CLASS_POSITIVE_SUBNORMAL = 7,
    MSF_CLASS_POSITIVE_NORMAL = 8,
    MSF_CLASS_POSITIVE_INFINITY = 9
} msf_class_t;

/* Decimal character conversion specification (SF-0 Section 2.6):
 * precision = significant digits (<= 0 selects the format's Pmin);
 * style = selector below; min_digits = minimum digit count to emit.
 * Exact field semantics are the Wave 3 gate's to freeze. */
enum {
    MSF_DECIMAL_STYLE_SCIENTIFIC = 0,
    MSF_DECIMAL_STYLE_FIXED = 1
};
typedef struct msf_decimal_spec {
    int precision;
    int style;
    int min_digits;
} msf_decimal_spec_t;

/* Hexadecimal-significand output: precision < 0 = exact-enough. */
typedef struct msf_hex_spec {
    int precision;
} msf_hex_spec_t;

/* Correctly rounded decimal digit limit H (SF-0 Section 2.6). */
#define MSF_DECIMAL_H 20

"""


def emit_public_header(ops):
    lines = [HEADER_PRELUDE]
    for o in ops:
        lines.append("/* %s (754-2019 %s), wave %d, %s */" %
                     (o["std_name"], o["clause"], o["wave"], o["status"]))
        lines.append(o["decl"])
    lines.append("\n#endif /* MUSE_SOFTFLOAT_H */\n")
    return "\n".join(lines)


def emit_formats_header():
    lines = ["""/* msf_formats.h - internal per-format constants.
 * GENERATED by tools/gen_tables.py from tables/formats.tsv.
 * Do not edit: the runner refuses drift (SF-0 Section 6 item 3).
 * Derived per format: trailing bits t = bits-1-w; bias = emax =
 * 2^(w-1)-1; emin = 1-emax; default quiet NaN = positive, exponent
 * all ones, quiet bit (top trailing bit) set, rest zero (SF-0 2.5).
 */
#ifndef MSF_FORMATS_H
#define MSF_FORMATS_H

"""]
    for f in FORMATS:
        bits, p, w, pmin = int(f["bits"]), int(f["p"]), int(f["w"]), int(f["pmin"])
        t = bits - 1 - w
        assert t == p - 1, f
        emax = (1 << (w - 1)) - 1
        pre = "MSF_" + f["name"].upper()
        sign = 1 << (bits - 1)
        expmax = (1 << w) - 1
        frac = (1 << t) - 1
        inf = expmax << t
        qnan = inf | (1 << (t - 1))
        hx = lambda v: "0x%0*xULL" % ((bits + 3) // 4, v)
        lines.append(
            "#define %s_BITS %d\n"
            "#define %s_PRECISION %d\n"
            "#define %s_EXP_BITS %d\n"
            "#define %s_FRAC_BITS %d\n"
            "#define %s_BIAS %d\n"
            "#define %s_EMAX %d\n"
            "#define %s_EMIN (%d)\n"
            "#define %s_PMIN %d\n"
            "#define %s_SIGN_MASK %s\n"
            "#define %s_EXP_MAX %s\n"
            "#define %s_FRAC_MASK %s\n"
            "#define %s_INFINITY %s\n"
            "#define %s_QUIET_BIT %s\n"
            "#define %s_DEFAULT_QNAN %s\n" %
            (pre, bits, pre, p, pre, w, pre, t, pre, emax, pre, emax,
             pre, 1 - emax, pre, pmin, pre, hx(sign), pre, hx(expmax),
             pre, hx(frac), pre, hx(inf), pre, hx(1 << (t - 1)), pre, hx(qnan)))
    lines.append("\n#endif /* MSF_FORMATS_H */\n")
    return "\n".join(lines)


SIGS = ["rint_named", "rint_exact", "next", "remainder", "scaleb", "logb",
        "arith_bin", "arith_un", "fma", "from_int", "to_int", "conv_fmt",
        "char_from", "char_to_dec", "char_to_hex", "sign_un", "sign_bin",
        "compare", "totalorder", "classify", "class_op", "radix_op",
        "version_op", "flag_op"]
KINDS = ["F16", "F32", "F64", "I8", "U8", "I16", "U16", "I32", "U32",
         "I64", "U64", "BOOL", "CLASS", "INT", "SPECIAL"]


def emit_dispatch(ops):
    lines = ["""/* msf_dispatch.h - runner dispatch over every instantiation.
 * GENERATED by tools/gen_tables.py. Do not edit: drift is refused.
 * call is a correctly typed trampoline over the real function,
 * bound only for implemented, vector-replayable instantiations
 * (status from tables/implemented.tsv); planned entries carry NULL
 * and the runner reports them not-implemented BY NAME (never as
 * passes). RETKIND/ARGKIND drive operand parsing and result
 * comparison widths in tests/runner.c.
 */
#ifndef MSF_DISPATCH_H
#define MSF_DISPATCH_H

#include <stdint.h>
#include "../include/muse_softfloat.h"

enum msf_sig {
%s
};
enum msf_kind {
    MSF_AK_NONE = 0,
%s
};
typedef uint64_t (*msf_call_fn)(const uint64_t *args, int rm, msf_flags_t *flags);
typedef struct msf_op_desc {
    const char *name;
    const char *std_name;
    uint8_t sig;
    uint8_t retkind;
    uint8_t argkinds[3];
    uint8_t nargs;
    uint8_t has_rm;
    uint8_t has_flags;
    uint8_t status; /* 0 planned, 1 implemented */
    uint8_t wave;
    msf_call_fn call;
} msf_op_desc_t;

""" % (",\n".join("    MSF_SIG_%s = %d" % (s.upper(), n) for n, s in enumerate(SIGS)),
       ",\n".join("    MSF_AK_%s = %d, MSF_RK_%s = %d" % (k, 2 * n + 1, k, 2 * n + 1)
                   for n, k in enumerate(KINDS)))]
    for o in ops:
        w = wrapper_for(o)
        if w is not None:
            lines.append(w)
    lines.append("\nstatic const msf_op_desc_t MSF_OPS[] = {")
    for o in ops:
        aks = o["argkinds"] + ["MSF_AK_NONE"] * (3 - len(o["argkinds"]))
        lines.append('    { "%s", "%s", MSF_SIG_%s, %s, { %s }, %d, %d, %d, %d, %d, %s },' %
                     (o["name"], o["std_name"], o["sig"].upper(), o["retkind"],
                      ", ".join(aks), len(o["argkinds"]),
                      1 if o["rounding"] == "attr" else 0,
                      1 if o["flags"] == "yes" else 0,
                      1 if o["status"] == "implemented" else 0,
                      o["wave"],
                      "msf_call_%s" % o["name"] if wrapper_for(o) is not None else "0"))
    lines.append("};\n#define MSF_OP_COUNT %d\n\n#endif /* MSF_DISPATCH_H */\n" % len(ops))
    return "\n".join(lines)


def emit_coverage(ops):
    lines = ["# COVERAGE.tsv - per-instantiation coverage ledger (SF-0 4.3).",
             "# GENERATED by tools/gen_tables.py from tables/. One row per",
             "# instantiation. No row may read authority=unconfirmed at a",
             "# wave gate. status=implemented means the core provides the",
             "# function today; claiming conformance additionally needs the",
             "# wave gate named in the wave column to have closed.",
             "name\tstd_name\tclause\tdest\tsources\trounding\tflags\twave\tstatus\tauthority\tvectors\tcomparison"]
    for o in ops:
        lines.append("\t".join([o["name"], o["std_name"], o["clause"], o["dest"],
                                o["sources"], o["rounding"], o["flags"],
                                str(o["wave"]), o["status"], o["authority"],
                                o["vectors"], o["comparison"]]))
    return "\n".join(lines) + "\n"


def main(argv):
    outdir = pathlib.Path(argv[1]) if len(argv) > 1 else ROOT
    ops = instantiate()
    targets = {
        "include/muse_softfloat.h": emit_public_header(ops),
        "src/msf_formats.h": emit_formats_header(),
        "tests/msf_dispatch.h": emit_dispatch(ops),
        "docs/COVERAGE.tsv": emit_coverage(ops),
    }
    for rel, text in targets.items():
        path = outdir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        print("wrote %s (%d bytes)" % (rel, len(text)))
    print("instantiations: %d (implemented %d)" %
          (len(ops), sum(1 for o in ops if o["status"] == "implemented")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
