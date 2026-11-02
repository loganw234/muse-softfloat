"""tokens-visual stills + HTML canvas + short mp4 (video/site idiom, 1920x1080)."""
import json, sys, math
sys.path.insert(0, 'C:/Users/logan/source/repos/Muse-Softfloat')
from video import style as S
from PIL import Image, ImageDraw
from datetime import datetime

ROOT = 'C:/Users/logan/source/repos/Muse-Softfloat/scratch/study-tokens-visual/'
D = json.load(open(ROOT + 'data/tokens.json'))
BILLED = D['grand']['billed']
OWN = D['headline']['owner_est']
B0, B1 = D['headline']['band']
STAMP = 'as of 2026-10-28 (PT) - no VCS in repo - regen: rerun aggregate.py + gen_data.py'
DEF1 = 'owner = chars/4 heuristic over 40 owner-typed lead prompts (+/-30%)'
DEF2 = 'project = API-billed input+output from model_completed logs (cached C input, not additive)'


def base(title, sub):
    im = Image.new('RGB', (S.W, S.H), S.BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, S.W, 200], fill=S.BG2)
    d.text((80, 40), title, font=S.font('black', 72), fill=S.INK)
    d.text((80, 125), sub, font=S.font('body', 34), fill=S.DIM)
    d.line([80, 915, S.W - 80, 915], fill=S.FAINT, width=2)
    d.text((80, 925), DEF1, font=S.font('body', 24), fill=S.DIM)
    d.text((80, 953), DEF2, font=S.font('body', 24), fill=S.DIM)
    d.text((80, 981), STAMP, font=S.font('mono_reg', 22), fill=S.FAINT)
    return im, d


def fmt(n):
    return format(n, ',')


# ---- still 1: scale bar + x1e6 zoom ----
im, d = base('WHO WROTE THE TOKENS?', 'one owner, 40 messages - vs - every model call the project billed')
d.text((80, 240), 'PROJECT  %s billed tokens (input+output)' % fmt(BILLED),
       font=S.font('bold', 36), fill=S.AMBER)
d.rectangle([80, 300, S.W - 80, 380], fill=(60, 42, 8))
d.rectangle([80, 300, S.W - 80, 380], outline=S.AMBER, width=3)
d.text((80, 395), 'HUMAN  ~%s tokens %s  (a 1-px sliver at this scale: see zoom)' % (
    fmt(OWN), str(D['headline']['band'])), font=S.font('bold', 36), fill=S.CYAN)
d.line([80, 470, S.W - 80, 470], fill=S.CYAN, width=2)
d.text((80, 490), 'x500,000 ZOOM of the left edge', font=S.font('bold', 36), fill=S.INK)
d.rectangle([80, 550, S.W - 80, 795], fill=(8, 30, 38))
zx0, zx1 = 100, 900
frac = OWN / BILLED * 5e5
hx = zx0 + frac * (zx1 - zx0)
d.rectangle([zx0, 570, hx, 660], fill=S.CYAN)
d.rectangle([zx0, 570, zx1, 660], outline=S.CYAN, width=2)
d.text((zx0, 680), 'YOU: ~%s tokens, band %s-%s' % (fmt(OWN), fmt(B0), fmt(B1)),
       font=S.font('black', 44), fill=S.CYAN)
d.text((zx0, 735), 'share 0.00013%%  |  ~1 : %s' % fmt(D['headline']['ratio_1_in_N']),
       font=S.font('mono', 32), fill=S.INK)
d.text((80, 820), 'the human input is real - and invisible at project scale',
       font=S.font('body', 34), fill=S.DIM)
im.save(ROOT + 'still_scale.png')
print('still_scale.png ok')

# ---- still 2: per-message ticks vs cumulative step curve ----
owner = json.load(open(ROOT + 'owner_prompts.json'))
waves = D['usage_jsonl_stale']['per_wave']
anchors = []  # (label, iso_end, cum_billed)
cum = 0
for w in ['wave0', 'wave1', 'wave2', 'wave3']:
    cum += waves[w]['in'] + waves[w]['out']
    anchors.append((w, D['usage_jsonl_stale']['span'][1] if w == 'wave3'
                    else None, cum))
# wave end times from report derivation (passes spans)
ends = {'wave0': '2026-10-26T11:31:29-07:00', 'wave1': '2026-10-27T06:35:52-07:00',
        'wave2': '2026-10-27T08:11:37-07:00', 'wave3': '2026-10-27T11:16:42-07:00'}
anchors = [(w, ends[w], waves[w]['in'] + waves[w]['out']) for w in ends]
cum = 0
cumpts = []
for w, e, b in anchors:
    cum += b
    cumpts.append((w, e, cum))
cumpts.append(('now (tree+3)', D['grand']['span'][1], BILLED))

im, d = base('40 MESSAGES vs THE WHOLE PROJECT', 'each owner tick: one typed prompt - curve: cumulative billed tokens')
X0, X1, Y0, Y1 = 120, S.W - 120, 300, 790
t0 = datetime.fromisoformat('2026-10-26T09:24:41-07:00').timestamp()
t1 = datetime.fromisoformat(D['grand']['span'][1]).timestamp()


def X(t):
    return X0 + (t - t0) / (t1 - t0) * (X1 - X0)


def Y(v):
    f = math.log10(v + 1) / math.log10(BILLED + 1)
    return Y1 - f * (Y1 - Y0)


d.rectangle([X0, Y0, X1, Y1], outline=S.FAINT, width=2)
prev = None
for i, (w, e, c) in enumerate(cumpts):
    t = datetime.fromisoformat(e).timestamp()
    x, y = X(t), Y(c)
    if prev:
        d.line([prev[0], prev[1], x, prev[1]], fill=S.AMBER, width=5)
        d.line([x, prev[1], x, y], fill=S.AMBER, width=5)
    else:
        d.line([X(t0), y, x, y], fill=S.AMBER, width=5)
    prev = (x, y)
    d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=S.AMBER)
    if i == len(cumpts) - 1:
        lx, ly = x - 430, y - 44
    else:
        lx = max(X0 + 4, min(x + 12, X1 - 420))
        ly = y - 40 if i % 2 == 0 else y + 12
    d.text((lx, ly), '%s %s' % (w, fmt(c)),
           font=S.font('mono_reg', 24), fill=S.AMBER)
for m in owner:
    t = m['ts'] / 1e6
    x = X(max(t0, min(t, t1)))
    d.line([x, Y0 - 60, x, Y0 - 8], fill=S.CYAN, width=4)
d.text((X0, Y0 - 110), '40 owner ticks (one per typed prompt, incl. 1 duplicate resend)',
       font=S.font('body', 28), fill=S.CYAN)
d.text((X0, Y1 + 14), 'log scale - steps land on wave aggregates; within-wave shape NOT reconstructed',
       font=S.font('body', 26), fill=S.DIM)
pw = D['owner']['per_wave']
mults = []
for w in ['wave0', 'wave1', 'wave2', 'wave3', 'post']:
    wd = pw[w]['words']
    pb = (waves[w]['in'] + waves[w]['out']) if w in waves else BILLED - cum
    mults.append('%s: %d words -> %s tok' % (w, wd, fmt(pb)))
d.text((X0, Y1 + 50), '  |  '.join(mults[:3]), font=S.font('mono_reg', 22), fill=S.DIM)
d.text((X0, Y1 + 78), '  |  '.join(mults[3:]), font=S.font('mono_reg', 22), fill=S.DIM)
im.save(ROOT + 'still_timeline.png')
print('still_timeline.png ok')

# ---- HTML canvas proof ----
html = """<!doctype html><html><head><meta charset="utf-8"><title>tokens visual proof</title>
<style>body{background:#090b14;color:#f0f4ff;font-family:sans-serif;margin:0}
#w{width:960px;margin:24px auto}canvas{background:#101424;display:block}
p{color:#949eb8;font-size:14px}</style></head><body><div id="w">
<h1>Who wrote the tokens?</h1>
<canvas id="c" width="960" height="540"></canvas>
<p><button id="z">zoom x1,000,000</button>
owner ~%s tokens [%s] vs project %s billed. %s. %s. %s</p>
</div><script>
const B=%d,O=%d;let zoom=false;
const c=document.getElementById('c'),x=c.getContext('2d');
document.getElementById('z').onclick=()=>{zoom=!zoom;draw();};
function draw(){x.fillStyle='#101424';x.fillRect(0,0,960,540);
x.fillStyle='#fbbf24';x.fillRect(40,120,880,60);
x.fillStyle='#94a3b8';x.font='20px sans-serif';
x.fillText('PROJECT '+B.toLocaleString()+' billed tokens',40,110);
if(!zoom){x.fillStyle='#22d3ee';x.fillRect(40,220,2,40);
x.fillText('HUMAN ~'+O.toLocaleString()+' (1-px sliver) - press zoom',60,260);}
else{const f=O/B*1e6;x.fillStyle='#22d3ee';x.fillRect(40,220,880*f,80);
x.fillStyle='#fff';x.font='28px sans-serif';
x.fillText('YOU: ~'+O.toLocaleString()+' tokens, share 0.00013%%, ~1:%s',60,340);}}
draw();</script></body></html>""" % (
    fmt(OWN), D['headline']['band'], fmt(BILLED), DEF1, DEF2, STAMP,
    BILLED, OWN, fmt(D['headline']['ratio_1_in_N']))
open(ROOT + 'tokens_canvas.html', 'w').write(html)
print('tokens_canvas.html ok')

# ---- mp4: 4 s zoom (120 frames) ----
import sys as _sys
if '--mp4' not in _sys.argv:
    print('stills+html done (pass --mp4 for video)')
    raise SystemExit(0)
import imageio.v2 as imageio
import numpy as np
frames = []
for i in range(120):
    t = i / 119.0
    f = 1 + (1e6 - 1) * (t ** 3)
    im2 = Image.new('RGB', (S.W, S.H), S.BG)
    e = ImageDraw.Draw(im2)
    e.rectangle([0, 0, S.W, 200], fill=S.BG2)
    e.text((80, 40), 'WHO WROTE THE TOKENS?', font=S.font('black', 72), fill=S.INK)
    e.text((80, 125), 'zooming to the human sliver (x%s)' % fmt(int(f)),
           font=S.font('body', 34), fill=S.DIM)
    e.rectangle([80, 400, S.W - 80, 480], fill=(60, 42, 8), outline=S.AMBER, width=3)
    wfrac = min(1.0, OWN / BILLED * f)
    e.rectangle([80, 400, 80 + wfrac * (S.W - 160), 480], fill=S.CYAN)
    e.text((80, 520), 'PROJECT %s  |  HUMAN ~%s %s' % (fmt(BILLED), fmt(OWN), D['headline']['band']),
           font=S.font('mono', 32), fill=S.INK)
    e.text((80, 1001), STAMP, font=S.font('mono_reg', 24), fill=S.FAINT)
    frames.append(np.asarray(im2))
imageio.mimsave(ROOT + 'tokens_zoom.mp4', frames, fps=30, codec='libx264',
                quality=8, macro_block_size=1)
print('tokens_zoom.mp4 ok')
