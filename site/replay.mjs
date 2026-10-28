// replay.mjs - replay the bundled committed-vector sample through the
// WebAssembly build and compare against the recorded expectations.
//
// Usage: node site/replay.mjs [site-dir]
// Exit 0 iff every sampled vector matches (result bits masked to the
// result-kind width, flags exact where the line records them - the
// same rules tests/runner.c applies for compare=exact files; the
// committed files carry no compare= directives, verified at base).
// Lines with masked ("~") expectations and the non-hex-drivable
// character/flag ops are excluded upstream by build_data.py.
import { readFileSync } from "node:fs";
import { join } from "node:path";

const dir = process.argv[2] || new URL(".", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1");
const wasmBytes = readFileSync(join(dir, "msf.wasm"));
const ops = JSON.parse(readFileSync(join(dir, "ops.json"), "utf8"));
const sample = JSON.parse(readFileSync(join(dir, "vectors-sample.json"), "utf8"));
const byName = new Map(ops.map((o) => [o.name, o]));
const RM = { te: 0, tz: 1, tp: 2, tn: 3, ta: 4, "-": -1 };

const { instance } = await WebAssembly.instantiate(wasmBytes, {});
const ex = instance.exports;
for (const k of ["msf_op_count", "msf_run", "msf_result_lo", "msf_result_hi", "msf_result_flags", "msf_result_ok"]) {
  if (typeof ex[k] !== "function") { console.error(`missing export ${k}`); process.exit(2); }
}
console.log(`msf_op_count=${ex.msf_op_count()} ops_json=${ops.length} sample=${sample.length}`);
if (ex.msf_op_count() !== ops.length) { console.error("op count mismatch wasm vs ops.json"); process.exit(2); }

const mask = (w) => (w >= 64 ? (1n << 64n) - 1n : (1n << BigInt(w)) - 1n);
let bad = 0;
const badShow = [];
for (const v of sample) {
  const op = byName.get(v.op);
  const words = [];
  for (let k = 0; k < 3; k++) {
    const bits = k < v.args.length ? BigInt("0x" + (v.args[k] || "0")) : 0n;
    words.push(Number(bits & 0xffffffffn) >>> 0, Number((bits >> 32n) & 0xffffffffn) >>> 0);
  }
  ex.msf_run(op.i, RM[v.rm], words[0], words[1], words[2], words[3], words[4], words[5]);
  if (!ex.msf_result_ok()) { bad++; badShow.push(`${v.op}: not runnable`); continue; }
  const got = (BigInt(ex.msf_result_hi() >>> 0) << 32n) | BigInt(ex.msf_result_lo() >>> 0);
  const want = BigInt("0x" + v.result);
  const m = mask(op.retw);
  const flagsOk = v.flags === "--" || ex.msf_result_flags() === parseInt(v.flags, 16);
  if ((got & m) !== (want & m) || !flagsOk) {
    bad++;
    if (badShow.length < 10) {
      badShow.push(`${v.op} ${v.rm} ${v.args.join(" ")} -> got ${(got & m).toString(16)}/${ex.msf_result_flags().toString(16)} want ${(want & m).toString(16)}/${v.flags} (${v.file} ${v.prov})`);
    }
  }
}
console.log(`replayed=${sample.length} mismatches=${bad}`);
for (const s of badShow) console.log("MISMATCH " + s);
process.exit(bad === 0 ? 0 : 1);
