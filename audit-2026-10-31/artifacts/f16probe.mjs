import fs from "fs";
const src = fs.readFileSync("/home/user/muse-softfloat/site/app.js","utf8");
const m = src.match(/function f16ToBits[\s\S]*?\n\}\n/);
if (!m) { console.log("could not locate f16ToBits in app.js"); process.exit(1); }
const f16ToBits = new Function(m[0] + "; return f16ToBits;")();
// reference: round-to-nearest-even half encoder via exact arithmetic on doubles
function ref(x){ if(x===0) return 0; let s=x<0?1:0; x=Math.abs(x); let e=Math.floor(Math.log2(x)); if (2**e>x) e--; if (2**(e+1)<=x) e++;
  let q; if (e < -14) { q = x/2**-24; let r=Math.floor(q), f=q-r; if (f>0.5||(f===0.5&&(r&1))) r++; return (s<<15)|r; }
  q = x/2**(e-10); let r=Math.floor(q), f=q-r; if (f>0.5||(f===0.5&&(r&1))) r++; if (r===2048){ r=1024; e++; } return (s<<15)|((e+15)<<10)|(r-1024); }
const probes=[1.00048828125, 2049, 2**-25, 2.5*2**-24, 1.5, 0.1, 65504, 3.14159, 1+2**-11, 1+3*2**-11];
let bad=0; for (const x of probes){ const a=f16ToBits(x), b=ref(x); const ok=(Number(a)===b); if(!ok) bad++; console.log(String(x).padEnd(24), "page=0x"+a.toString(16).padStart(4,"0"), "RNE=0x"+b.toString(16).padStart(4,"0"), ok?"":"  <-- DIFFERS"); }
console.log("differences:",bad,"of",probes.length);
