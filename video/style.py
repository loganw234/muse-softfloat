"""Single source of style truth: palette, type scale, fonts, beat grid.

Edit here to re-skin every scene. Nothing scene-specific lives in this file.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

W, H = 1920, 1080
FPS = 30

# Palette (RGB). Dark stage, hot accents; high energy, readable at a glance.
BG = (9, 11, 20)
BG2 = (16, 20, 36)
INK = (240, 244, 255)
DIM = (148, 158, 184)
FAINT = (70, 80, 110)
CYAN = (34, 211, 238)
AMBER = (251, 191, 36)
PINK = (244, 114, 182)
GREEN = (52, 211, 153)
RED = (248, 113, 113)
VIOLET = (167, 139, 250)

ACCENTS = [CYAN, AMBER, PINK, GREEN, VIOLET, (96, 165, 250), (45, 212, 191), (251, 146, 60)]

# Type scale (px at 1080p).
T_MEGA = 200
T_HERO = 132
T_H1 = 96
T_H2 = 64
T_BODY = 40
T_SMALL = 30
T_MONO = 32
T_TICKER = 34

FONT_DIR = Path(r"C:\Windows\Fonts")
_FONT_FILES = {
    "black": "arialbd.ttf",      # headlines
    "bold": "segoeuib.ttf",      # sub-heads
    "body": "segoeui.ttf",       # labels
    "mono": "consolab.ttf",      # numbers / ticker / hashes
    "mono_reg": "consola.ttf",
}


@lru_cache(maxsize=512)
def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    size = max(8, int(size))
    path = FONT_DIR / _FONT_FILES[kind]
    return ImageFont.truetype(str(path), size)


# Beat grid: hard cuts land on multiples of BEAT seconds (150 BPM eighth = 0.4s;
# scenes here cut on whole/half beats of a 120 BPM bar for readability).
BPM = 120
BEAT = 60.0 / BPM  # 0.5 s


def ease_out_cubic(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return 1.0 - (1.0 - x) ** 3


def ease_out_back(x: float, s: float = 1.70158) -> float:
    x = min(1.0, max(0.0, x))
    return 1.0 + (s + 1.0) * (x - 1.0) ** 3 + s * (x - 1.0) ** 2


def ease_in_out(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3.0 - 2.0 * x)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def blend(c1, c2, t: float):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))
