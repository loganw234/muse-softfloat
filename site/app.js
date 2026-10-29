"use strict";
/* muse-softfloat demo: drives site/msf.wasm (the repository's own
 * src/*.c, compiled unmodified) through the generated dispatch table.
 * If WebAssembly is unavailable, free entry is disabled and dealt
 * vectors show their recorded results, labelled as recorded. */

const RM_LABEL = ["ties to even", "toward zero", "toward +∞", "toward −∞", "ties to away"];
const RM_TOKEN = { te: 0, tz: 1, tp: 2, tn: 3, ta: 4, "-": -1 };
const CLASS_NAMES = ["signaling NaN", "quiet NaN", "−∞", "negative normal",
  "negative subnormal", "−0", "+0", "positive subnormal", "positive normal", "+∞"];
const FLAG_DEFS = [
  [0x01, "invalid"], [0x02, "division by zero"], [0x04, "overflow"],
  [0x08, "underflow"], [0x10, "inexact"],
];
const FLOAT_KIND = { F16: { w: 16, e: 5, t: 10 }, F32: { w: 32, e: 8, t: 23 }, F64: { w: 64, e: 11, t: 52 } };

const $ = (id) => document.getElementById(id);
const fmtInt = (n) => n.toLocaleString("en-US");

/* ---- bit/decimal display conversions (page-side, for display only) ---- */
const dv = new DataView(new ArrayBuffer(8));
function f64ToBits(x) { dv.setFloat64(0, x); return dv.getBigUint64(0); }
function bitsToF64(b) { dv.setBigUint64(0, b); return dv.getFloat64(0); }
function f32ToBits(x) { dv.setFloat32(0, x); return BigInt(dv.getUint32(0)); }
function bitsToF32(b) { dv.setUint32(0, Number(b & 0xffffffffn)); return dv.getFloat32(0); }

function bitsToF16(b) {
  const sign = (b >> 15n) & 1n, exp = Number((b >> 10n) & 0x1fn), frac = Number(b & 0x3ffn);
  let v;
  if (exp === 0) v = frac * 2 ** -24;
  else if (exp === 31) v = frac === 0 ? Infinity : NaN;
  else v = (1 + frac / 1024) * 2 ** (exp - 15);
  return sign ? -v : v;
}
function f16ToBits(x) {
  if (Number.isNaN(x)) return 0x7e00n;
  const sign = x < 0 || Object.is(x, -0) ? 0x8000n : 0n;
  x = Math.abs(x);
  if (x === Infinity) return sign | 0x7c00n;
  if (x === 0) return sign;
  let e = Math.floor(Math.log2(x));
  // value = m * 2^(e-10) with integer m in [1024, 2048) for normals.
  let m = Math.round(x / 2 ** (e - 10));
  if (m >= 2048) { m = 1024; e += 1; }
  if (e >= 16) return sign | 0x7c00n; // overflow to Inf at ties-to-even bound is good enough for entry
  if (e >= -14) return sign | (BigInt(e + 15) << 10n) | BigInt(m - 1024);
  // subnormal: value = f * 2^-24
  const f = Math.round(x / 2 ** -24);
  if (f >= 1024) return sign | (1n << 10n);
  return sign | BigInt(f);
}

function kindMask(w) { return w >= 64 ? (1n << 64n) - 1n : (1n << BigInt(w)) - 1n; }
function hexOf(bits, w) { return (bits & kindMask(w)).toString(16).padStart(Math.ceil(w / 4), "0"); }

function bitsToDecimal(kind, bits) {
  if (kind === "F16") return String(bitsToF16(bits));
  if (kind === "F32") return String(bitsToF32(bits));
  if (kind === "F64") return String(bitsToF64(bits));
  if (kind === "BOOL") return bits === 0n ? "false" : "true";
  if (kind === "CLASS") return CLASS_NAMES[Number(bits)] ?? String(bits);
  if (kind.startsWith("I")) {
    const w = BigInt(parseInt(kind.slice(1), 10));
    const v = bits & ((1n << w) - 1n);
    return String(v >= (1n << (w - 1n)) ? v - (1n << w) : v);
  }
  if (kind.startsWith("U")) {
    const w = BigInt(parseInt(kind.slice(1), 10));
    return String(bits & ((1n << w) - 1n));
  }
  if (kind === "INT") return String(BigInt.asIntN(64, bits));
  return "";
}
function decimalToBits(kind, text) {
  text = text.trim();
  if (kind in FLOAT_KIND) {
    const x = text === "inf" || text === "Infinity" ? Infinity
      : text === "-inf" || text === "-Infinity" ? -Infinity
      : text.toLowerCase() === "nan" ? NaN : Number(text);
    if (text !== "" && Number.isNaN(x) && text.toLowerCase() !== "nan") return null;
    if (kind === "F16") return f16ToBits(x);
    if (kind === "F32") return f32ToBits(x);
    return f64ToBits(x);
  }
  try { return BigInt(text); } catch { return null; }
}
function parseHex(text) {
  const t = text.trim().replace(/^0x/i, "");
  if (!/^[0-9a-fA-F]*$/.test(t)) return null;
  return t === "" ? 0n : BigInt("0x" + t);
}

/* ---- state ---- */
let OPS = [], SAMPLE = [], DATA = null, wasm = null;
let operandRows = []; // {hex, dec, decoded, kind, width}
let lastDealt = null;

const fmtSel = $("fmt"), opSel = $("op"), rmSel = $("rm");

function formatGroup(op) {
  if (op.name.startsWith("msf16_")) return "f16";
  if (op.name.startsWith("msf32_")) return "f32";
  if (op.name.startsWith("msf64_")) return "f64";
  return "general";
}
function currentOp() { return OPS[Number(opSel.value)]; }

function fillOps(preferName) {
  const g = fmtSel.value;
  opSel.innerHTML = "";
  for (const op of OPS) {
    if (!op.runnable || formatGroup(op) !== g) continue;
    const o = document.createElement("option");
    o.value = String(op.i);
    o.textContent = `${op.std} — ${op.name}`;
    opSel.appendChild(o);
  }
  if (preferName) {
    const t = OPS.find((o) => o.name === preferName);
    if (t) opSel.value = String(t.i);
  }
  syncOpUI();
}

function syncOpUI() {
  const op = currentOp();
  if (!op) return;
  rmSel.disabled = !op.rm;
  $("op-note").textContent =
    `${op.name} · Clause ${op.clause || "—"} · Tier ${op.tier || "—"} · ` +
    (op.rm ? "rounding attribute applies" : "rounding is named in the operation") +
    (op.flags ? " · raises flags" : " · no flags");
  buildOperands(op);
}

function buildOperands(op) {
  const host = $("operands");
  host.innerHTML = "";
  operandRows = op.args.map((kind, k) => {
    const width = op.argw[k];
    const row = document.createElement("div");
    row.className = "operand";
    const def = defaultOperand(kind);
    row.innerHTML =
      `<label class="hex">Operand ${"abc"[k]} · ${kind} bits (hex)` +
      `<input type="text" spellcheck="false" value="${hexOf(def, width)}"></label>` +
      `<label class="dec">Decimal<input type="text" spellcheck="false"></label>` +
      `<span class="decoded"></span>`;
    host.appendChild(row);
    const hex = row.querySelector(".hex input");
    const dec = row.querySelector(".dec input");
    const decoded = row.querySelector(".decoded");
    const entry = { hex, dec, decoded, kind, width };
    hex.addEventListener("input", () => syncFromHex(entry));
    dec.addEventListener("input", () => syncFromDec(entry));
    syncFromHex(entry);
    return entry;
  });
}

function defaultOperand(kind) {
  if (kind === "F16") return 0x3c00n;            // 1.0
  if (kind === "F32") return 0x3f800000n;        // 1.0
  if (kind === "F64") return 0x3ff0000000000000n; // 1.0
  return 1n;
}
function syncFromHex(entry) {
  const bits = parseHex(entry.hex.value);
  if (bits === null) { entry.decoded.textContent = "not hex"; return; }
  const masked = bits & kindMask(entry.width);
  entry.dec.value = bitsToDecimal(entry.kind, masked);
  entry.decoded.textContent = `= ${entry.dec.value}`;
}
function syncFromDec(entry) {
  const bits = decimalToBits(entry.kind, entry.dec.value);
  if (bits === null) { entry.decoded.textContent = "not a number"; return; }
  entry.hex.value = hexOf(bits, entry.width);
  entry.decoded.textContent = `bits ${entry.hex.value}`;
}
function operandBits() {
  const out = [0n, 0n, 0n];
  operandRows.forEach((r, k) => {
    const b = parseHex(r.hex.value);
    out[k] = (b === null ? 0n : b) & kindMask(r.width);
  });
  return out;
}

/* ---- running ---- */
function runWasm(op, rm, bits) {
  const w = [];
  for (let k = 0; k < 3; k++) {
    w.push(Number(bits[k] & 0xffffffffn) >>> 0,
           Number((bits[k] >> 32n) & 0xffffffffn) >>> 0);
  }
  wasm.msf_run(op.i, rm, w[0], w[1], w[2], w[3], w[4], w[5]);
  if (!wasm.msf_result_ok()) return null;
  return {
    result: (BigInt(wasm.msf_result_hi() >>> 0) << 32n) | BigInt(wasm.msf_result_lo() >>> 0),
    flags: wasm.msf_result_flags(),
  };
}

function showResult(op, result, flags, recorded) {
  $("result").hidden = false;
  const masked = result & kindMask(op.retw);
  $("res-kind").textContent = recorded ? `${op.ret} (recorded)` : op.ret;
  $("res-hex").textContent = "0x" + hexOf(masked, op.retw);
  const dec = bitsToDecimal(op.ret, masked);
  $("res-dec").textContent = dec === "" ? "" : `= ${dec}`;
  renderBits(op, masked);
  const host = $("res-flags");
  host.innerHTML = "";
  if (!op.flags || flags === null) {
    host.innerHTML = `<span class="chip na">this operation reports no flags</span>`;
    return;
  }
  for (const [bit, label] of FLAG_DEFS) {
    const c = document.createElement("span");
    c.className = "chip" + (flags & bit ? " on" : "");
    c.textContent = label;
    host.appendChild(c);
  }
}

function renderBits(op, bits) {
  const host = $("res-bits"), fields = $("res-fields");
  const f = FLOAT_KIND[op.ret];
  const bitStr = bits.toString(2).padStart(op.retw, "0");
  if (!f) {
    host.textContent = bitStr.replace(/(.{4})(?=.)/g, "$1 ");
    fields.textContent = op.ret === "CLASS" ? "the ten classes of IEEE 754 §5.7.2, as an integer"
      : op.ret === "BOOL" ? "predicate result" : "integer result bits";
    return;
  }
  const parts = [
    ["sign", bitStr.slice(0, 1)],
    ["exp", bitStr.slice(1, 1 + f.e)],
    ["frac", bitStr.slice(1 + f.e)],
  ];
  host.innerHTML = parts.map(([cls, s], pi) =>
    (pi ? `<span class="gap"></span>` : "") +
    [...s].map((ch) => `<span class="b ${cls}">${ch}</span>`).join("")).join("");
  const sign = Number((bits >> BigInt(f.w - 1)) & 1n);
  const expRaw = Number((bits >> BigInt(f.t)) & BigInt(2 ** f.e - 1));
  const bias = 2 ** (f.e - 1) - 1;
  const frac = bits & ((1n << BigInt(f.t)) - 1n);
  const expTxt = expRaw === 2 ** f.e - 1
    ? (frac === 0n ? "∞ / NaN field" : "NaN field")
    : expRaw === 0 ? `biased 0 (zero/subnormal, exponent ${1 - bias})`
    : `biased ${expRaw} (exponent ${expRaw - bias})`;
  fields.innerHTML =
    `<span class="sw sw-sign"></span>sign ${sign} &nbsp; ` +
    `<span class="sw sw-exp"></span>exponent ${expTxt} &nbsp; ` +
    `<span class="sw sw-frac"></span>significand field 0x${frac.toString(16)}`;
}

function doRun() {
  const op = currentOp();
  if (!op || !wasm) return;
  const rm = op.rm ? Number(rmSel.value) : -1;
  const r = runWasm(op, rm, operandBits());
  if (r) showResult(op, r.result, r.flags, false);
}

function doDeal() {
  if (!SAMPLE.length) return;
  const v = SAMPLE[Math.floor(Math.random() * SAMPLE.length)];
  lastDealt = v;
  const op = OPS.find((o) => o.name === v.op);
  fmtSel.value = formatGroup(op);
  fillOps(v.op);
  if (op.rm && RM_TOKEN[v.rm] >= 0) rmSel.value = String(RM_TOKEN[v.rm]);
  operandRows.forEach((row, k) => {
    row.hex.value = hexOf(BigInt("0x" + (v.args[k] || "0")), row.width);
    syncFromHex(row);
  });
  const line = `${v.op} ${v.rm} ${v.args.join(" ")} -> ${v.result} ${v.flags} ${v.prov}`;
  const dealt = $("dealt");
  dealt.hidden = false;
  if (wasm) {
    const bits = [0n, 1n, 2n].map((k) => BigInt("0x" + (v.args[Number(k)] || "0")));
    const r = runWasm(op, RM_TOKEN[v.rm], bits);
    const m = kindMask(op.retw);
    const okRes = r && (r.result & m) === (BigInt("0x" + v.result) & m);
    const okFlags = v.flags === "--" || (r && r.flags === parseInt(v.flags, 16));
    const ok = Boolean(okRes && okFlags);
    dealt.innerHTML =
      `Dealt from <b>tests/vectors/${v.file}</b>:<br>${line}<br>` +
      `<span class="verdict ${ok ? "match" : "mismatch"}">${ok
        ? "MATCH — the WebAssembly build just reproduced this recorded result and flags live."
        : "MISMATCH — this would be a defect; the build-time replay requires zero of these."}</span>`;
    if (r) showResult(op, r.result, r.flags, false);
  } else {
    dealt.innerHTML =
      `Dealt from <b>tests/vectors/${v.file}</b>:<br>${line}<br>` +
      `<span class="verdict recorded">Recorded result shown — live computation is unavailable ` +
      `because the WebAssembly build did not load in this browser.</span>`;
    showResult(op, BigInt("0x" + v.result),
               v.flags === "--" ? null : parseInt(v.flags, 16), true);
  }
}

/* ---- generated tables ---- */
function renderNumbers() {
  const d = DATA;
  $("status-line").textContent =
    `Status at ${d.base}: ${fmtInt(d.instantiations.implemented)} of ` +
    `${fmtInt(d.instantiations.total)} instantiations implemented and gated · ` +
    `${fmtInt(d.vectors.total)} committed test vectors · ` +
    `planted-copy score ${d.plants.caught} of ${d.plants.total}`;
  const rows = [
    ["Instantiations (operation × format × operand kinds)", fmtInt(d.instantiations.total), d.instantiations.source],
    ["…of which Tier 1 (Clause 5 surface)", fmtInt(d.instantiations.tier1), d.instantiations.source],
    ["…of which Tier 2 (complete at SF-2 close)", fmtInt(d.instantiations.tier2), d.instantiations.source],
    ["Implemented", fmtInt(d.instantiations.implemented), d.instantiations.source],
    ["Committed test vectors", fmtInt(d.vectors.total), d.vectors.source],
    ["Vector files", fmtInt(Object.keys(d.vectors.files).length), d.vectors.source],
    ["Operations runnable in this page", `${fmtInt(d.sample.ops_runnable)} of ${fmtInt(d.sample.ops_total)}`, "tests/msf_dispatch.h"],
    ["Augmented pair operations excluded here (head+tail results; see the instrument note)",
     `${fmtInt(d.sample.ops_pair_excluded)} (host/board gated)`, "tests/msf_dispatch.h"],
    ["Bundled vectors replayed through the WASM build at build time",
     `${fmtInt(d.sample.vectors)} (0 mismatches required)`, "site/replay-log.txt"],
    ["Operations covered by that replay", fmtInt(d.sample.ops_covered), d.sample.source],
    ["Planted defects caught by independent verifiers",
     `${d.plants.caught} of ${d.plants.total}`, d.plants.source],
  ];
  $("numbers-table").querySelector("tbody").innerHTML = rows.map(
    ([m, v, s]) => `<tr><td>${m}</td><td class="num">${v}</td><td class="src">${s}</td></tr>`).join("");
  $("plants-table").querySelector("tbody").innerHTML = d.plants.by_wave.map((r) =>
    `<tr><td>${r.wave}</td><td class="num">${r.caught}</td><td class="num">${r.total}</td>` +
    `<td><div class="bar-bg"><div class="bar" style="width:${(100 * r.caught / r.total).toFixed(1)}%"></div></div></td></tr>`).join("");
  $("build-stamp").textContent =
    `Site data generated from commit ${d.base} by site/build_data.py · ` +
    `library compiled to WebAssembly from the same tree (site/build.py).`;
}

/* ---- IAS15 figure-8 illustration (carries no data) ---- */
function drawOrbit() {
  const c = $("orbit");
  if (!c) return;
  const ctx = c.getContext("2d");
  const W = c.width, H = c.height, cx = W / 2, cy = H / 2;
  // A lemniscate-like path; three bodies chase along it, equally spaced.
  const pos = (t) => {
    const s = Math.sin(t), denom = 1 + s * s;
    return [cx + (W * 0.36) * Math.cos(t) / denom * 1.6,
            cy + (H * 0.30) * (s * Math.cos(t)) / denom * 1.6];
  };
  const trace = () => {
    ctx.strokeStyle = "#cfd6d2"; ctx.lineWidth = 1; ctx.beginPath();
    for (let i = 0; i <= 240; i++) {
      const [x, y] = pos((i / 240) * 2 * Math.PI);
      i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
    }
    ctx.stroke();
  };
  const bodies = (phase) => {
    ctx.clearRect(0, 0, W, H);
    trace();
    ctx.fillStyle = "#1b201d";
    for (let b = 0; b < 3; b++) {
      const [x, y] = pos(phase + (b * 2 * Math.PI) / 3);
      ctx.beginPath(); ctx.arc(x, y, 5, 0, 2 * Math.PI); ctx.fill();
    }
    ctx.fillStyle = "#3d4541"; ctx.font = "11px sans-serif";
    ctx.fillText("illustration — not simulation output", 8, H - 8);
  };
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) { bodies(0.6); return; }
  let t0 = null;
  const step = (ts) => {
    if (t0 === null) t0 = ts;
    bodies(((ts - t0) / 9000) * 2 * Math.PI);
    requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

/* ---- init ---- */
async function init() {
  const status = $("wasm-status");
  try {
    [DATA, OPS, SAMPLE] = await Promise.all([
      fetch("data.json").then((r) => r.json()),
      fetch("ops.json").then((r) => r.json()),
      fetch("vectors-sample.json").then((r) => r.json()),
    ]);
    renderNumbers();
    fillOps("msf32_add");
  } catch (e) {
    status.textContent = "Site data failed to load (" + e.message + ").";
    status.className = "wasm-status down";
    return;
  }
  fmtSel.addEventListener("change", () => fillOps());
  opSel.addEventListener("change", syncOpUI);
  $("run").addEventListener("click", doRun);
  $("deal").addEventListener("click", doDeal);
  drawOrbit();
  try {
    const bytes = await fetch("msf.wasm").then((r) => {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.arrayBuffer();
    });
    const { instance } = await WebAssembly.instantiate(bytes, {});
    wasm = instance.exports;
    const n = wasm.msf_op_count();
    status.textContent =
      `WebAssembly build ready — the actual library, compiled to WebAssembly ` +
      `(${fmtInt(n)} dispatch entries; ${fmtInt(OPS.filter((o) => o.runnable).length)} runnable here). ` +
      `Proven at build time by replaying ${fmtInt(SAMPLE.length)} bundled committed vectors under Node.`;
    status.className = "wasm-status ok";
    doRun();
  } catch (e) {
    wasm = null;
    $("run").disabled = true;
    status.textContent =
      "WebAssembly build unavailable in this browser (" + e.message + "). " +
      "Free entry is disabled; “Deal me a committed vector” shows recorded results " +
      "from the repository's test vectors, labelled as recorded — no live computation.";
    status.className = "wasm-status down";
  }
}
init();
