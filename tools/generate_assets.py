#!/usr/bin/env python3
"""Procedural brand asset generator for the Ora landing page.

Pure PIL (no numpy): fields are computed at low resolution with Python
loops, then upscaled and blurred — which is exactly what soft aura
gradients want anyway. Outputs land in assets/gen/.
"""

import math
import os
import random
import struct

from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "gen")
os.makedirs(OUT, exist_ok=True)

random.seed(7)

# Brand palette
DEEP = (5, 9, 19)          # #050913 deep space navy
BLUE = (123, 183, 255)     # #7bb7ff electric blue
VIOLET = (148, 119, 255)   # violet
TEAL = (95, 227, 192)      # teal
EMBER = (255, 157, 111)    # warm ember accent


def lerp(a, b, t):
    return a + (b - a) * t


def save_webp(img, name, quality=82):
    path = os.path.join(OUT, name)
    img.save(path, "WEBP", quality=quality, method=6)
    print(f"wrote {path} ({os.path.getsize(path)//1024} KB)")


def radial_blob(size, cx, cy, radius, color, power=2.2, amp=1.0):
    """Additive radial glow layer as float buffer."""
    w, h = size
    buf = [[0.0, 0.0, 0.0] for _ in range(w * h)]
    for y in range(h):
        for x in range(w):
            d = math.hypot((x - cx) / radius, (y - cy) / radius)
            v = max(0.0, 1.0 - d)
            v = (v ** power) * amp
            i = y * w + x
            buf[i][0] = color[0] * v
            buf[i][1] = color[1] * v
            buf[i][2] = color[2] * v
    return buf


def add_buf(dst, src):
    for i in range(len(dst)):
        dst[i][0] += src[i][0]
        dst[i][1] += src[i][1]
        dst[i][2] += src[i][2]


def buf_to_img(buf, size, base=DEEP):
    w, h = size
    px = []
    for i in range(w * h):
        r = base[0] + buf[i][0]
        g = base[1] + buf[i][1]
        b = base[2] + buf[i][2]
        # soft-clip highlights so glows roll off filmically
        px.append((
            int(255 * (1 - math.exp(-r / 160.0))),
            int(255 * (1 - math.exp(-g / 160.0))),
            int(255 * (1 - math.exp(-b / 160.0))),
        ))
    img = Image.new("RGB", size)
    img.putdata(px)
    return img


def grain_tile(size=320, alpha=255):
    """Monochrome noise tile used as a CSS overlay."""
    img = Image.new("L", (size, size))
    img.putdata([random.randint(0, 255) for _ in range(size * size)])
    return img


def hero_nebula():
    """Main cinematic hero background: layered aura nebula."""
    w, h = 640, 400
    buf = [[0.0, 0.0, 0.0] for _ in range(w * h)]
    layers = [
        # (cx, cy, radius, color, power, amp)
        (w * 0.74, h * 0.62, 340, BLUE, 2.6, 1.05),
        (w * 0.88, h * 0.30, 250, VIOLET, 2.4, 0.85),
        (w * 0.58, h * 0.95, 280, TEAL, 3.0, 0.5),
        (w * 0.16, h * 0.18, 260, VIOLET, 3.2, 0.35),
        (w * 0.05, h * 0.85, 220, BLUE, 3.0, 0.30),
        (w * 0.70, h * 0.52, 90, (235, 244, 255), 2.0, 0.9),  # hot core
        (w * 0.30, h * 0.40, 150, EMBER, 3.4, 0.16),
    ]
    for cx, cy, radius, color, power, amp in layers:
        add_buf(buf, radial_blob((w, h), cx, cy, radius, color, power, amp))
    img = buf_to_img(buf, (w, h))
    img = img.resize((2400, 1500), Image.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(6))
    save_webp(img, "aura-nebula.webp", quality=80)
    # Mobile crop biased toward the hot core
    save_webp(img.crop((900, 0, 2100, 1500)).resize((960, 1200), Image.LANCZOS),
              "aura-nebula-mobile.webp", quality=78)


def orb(name, color, secondary, size_out=900):
    """Glowing orb with ring, alpha background — for parallax float layers."""
    w = h = 300
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    cx = cy = w / 2
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy) / (w * 0.5)
            if d >= 1.0:
                continue
            glow = max(0.0, 1.0 - d) ** 2.6
            ring = math.exp(-((d - 0.62) ** 2) / 0.004) * 0.85
            core = max(0.0, 1.0 - d / 0.30) ** 2.0
            a = min(1.0, glow * 0.9 + ring + core)
            r = lerp(color[0], secondary[0], min(1.0, d * 1.3)) + 120 * core
            g = lerp(color[1], secondary[1], min(1.0, d * 1.3)) + 120 * core
            b = lerp(color[2], secondary[2], min(1.0, d * 1.3)) + 120 * core
            px[x, y] = (int(min(255, r)), int(min(255, g)), int(min(255, b)),
                        int(255 * a))
    img = img.resize((size_out, size_out), Image.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(2))
    save_webp(img, name, quality=80)


def contour_field():
    """Aura rings: wobbling concentric contours, alpha bg.

    Reads as a 'living model' — organic data made visible.
    """
    w = h = 900
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    # Angular perturbation harmonics shared by all rings
    harm = [(k, random.uniform(0.008, 0.030), random.uniform(0, 6.28))
            for k in (2, 3, 5, 7)]
    rings = 11
    sigma = 0.0035
    for y in range(h):
        v = y / h - 0.5
        for x in range(w):
            u = x / w - 0.5
            r = math.hypot(u, v) * 2.0
            if r > 1.04 or r < 0.04:
                continue
            th = math.atan2(v, u)
            wob = sum(a * math.sin(k * th + p + r * 5.0) for k, a, p in harm)
            val = (r + wob) * rings
            t = val % 1.0
            d = min(t, 1.0 - t)
            line = math.exp(-(d * d) / sigma)
            if line < 0.03:
                continue
            mix = (math.sin(val * 0.9 + 1.0) + 1) / 2
            cr = lerp(BLUE[0], TEAL[0], mix)
            cg = lerp(BLUE[1], TEAL[1], mix)
            cb = lerp(BLUE[2], TEAL[2], mix)
            fade = max(0.0, 1.0 - r) ** 0.55
            a = 255 * line * fade
            if a < 4:
                continue
            px[x, y] = (int(cr), int(cg), int(cb), int(a))
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    img = img.resize((1100, 1100), Image.LANCZOS)
    save_webp(img, "aura-contours.webp", quality=80)


def ribbon():
    """Flowing horizontal energy ribbon with alpha — section divider art."""
    w, h = 1200, 360
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    strands = []
    for i in range(5):
        strands.append({
            "base": h * (0.30 + 0.10 * i),
            "amp": random.uniform(28, 70),
            "freq": random.uniform(1.4, 2.6),
            "ph": random.uniform(0, 6.28),
            "wid": random.uniform(10, 26),
            "col": [BLUE, VIOLET, TEAL, BLUE, VIOLET][i],
        })
    for x in range(w):
        u = x / w
        edge = math.sin(u * math.pi) ** 0.6  # fade at both ends
        for s in strands:
            yc = s["base"] + s["amp"] * math.sin(u * s["freq"] * 6.28 + s["ph"]) \
                 + 18 * math.sin(u * 9.4 + s["ph"] * 2)
            wid = s["wid"] * (0.7 + 0.3 * math.sin(u * 12 + s["ph"]))
            y0 = max(0, int(yc - wid * 3))
            y1 = min(h - 1, int(yc + wid * 3))
            for y in range(y0, y1 + 1):
                a = math.exp(-((y - yc) ** 2) / (2 * wid * wid)) * edge * 0.75
                if a < 0.02:
                    continue
                pr, pg, pb, pa = px[x, y]
                na = a * 255
                px[x, y] = (
                    min(255, pr + int(s["col"][0] * a)),
                    min(255, pg + int(s["col"][1] * a)),
                    min(255, pb + int(s["col"][2] * a)),
                    min(255, int(pa + na)),
                )
    img = img.resize((2400, 720), Image.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(1.5))
    save_webp(img, "aura-ribbon.webp", quality=80)


def noise_png():
    g = grain_tile(280)
    path = os.path.join(OUT, "grain.png")
    g.save(path, "PNG", optimize=True)
    print(f"wrote {path} ({os.path.getsize(path)//1024} KB)")


if __name__ == "__main__":
    noise_png()
    hero_nebula()
    orb("orb-blue.webp", BLUE, VIOLET)
    orb("orb-teal.webp", TEAL, BLUE, size_out=700)
    contour_field()
    ribbon()
    print("done")
