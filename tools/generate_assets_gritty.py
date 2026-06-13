#!/usr/bin/env python3
"""Athletic/gritty brand asset generator for the Ora landing page.

Iron, chalk, hard light — with the electric-blue aura kept as the brand
accent. Pure PIL. Outputs land in assets/gen/.
"""

import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "gen")
os.makedirs(OUT, exist_ok=True)

random.seed(11)

IRON = (9, 9, 12)
CHALK = (232, 230, 225)
BLUE = (123, 183, 255)
TEAL = (95, 227, 192)
EMBER = (255, 122, 69)

FONT_BOLD = "/tmp/SpaceGrotesk-Bold.ttf"
FONT_MED = "/tmp/SpaceGrotesk-Medium.ttf"
FONT_SERIF_IT = "/tmp/InstrumentSerif-Italic.ttf"


def save_webp(img, name, quality=82):
    path = os.path.join(OUT, name)
    img.save(path, "WEBP", quality=quality, method=6)
    print(f"wrote {path} ({os.path.getsize(path)//1024} KB)")


def streak_texture(size, strength=18, horizontal=True):
    """Brushed-iron streaks: low-res noise stretched along one axis."""
    w, h = size
    if horizontal:
        small = Image.new("L", (w // 24, h // 2))
    else:
        small = Image.new("L", (w // 2, h // 24))
    small.putdata([random.randint(0, 255) for _ in range(small.width * small.height)])
    tex = small.resize(size, Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2))
    # center on zero so it both lightens and darkens
    return tex.point(lambda v: int((v - 128) * strength / 128 + 128))


def apply_centered_overlay(base, tex):
    """Overlay a 128-centered L texture onto an RGB image (soft light-ish)."""
    px = base.load()
    tp = tex.load()
    w, h = base.size
    for y in range(h):
        for x in range(w):
            d = tp[x, y] - 128
            r, g, b = px[x, y]
            px[x, y] = (max(0, min(255, r + d)), max(0, min(255, g + d)),
                        max(0, min(255, b + d)))
    return base


def radial_glow(size, cx, cy, radius, color, amp, power=2.4):
    """RGB additive glow layer."""
    w, h = size
    layer = Image.new("RGB", size, (0, 0, 0))
    px = layer.load()
    x0, x1 = max(0, int(cx - radius)), min(w, int(cx + radius))
    y0, y1 = max(0, int(cy - radius)), min(h, int(cy + radius))
    for y in range(y0, y1):
        for x in range(x0, x1):
            d = math.hypot(x - cx, y - cy) / radius
            if d >= 1.0:
                continue
            v = ((1.0 - d) ** power) * amp
            px[x, y] = (int(color[0] * v), int(color[1] * v), int(color[2] * v))
    return layer


def light_shaft(size, x_top, width_top, x_bot, width_bot, color, amp):
    """Soft volumetric light wedge."""
    w, h = size
    layer = Image.new("L", size, 0)
    d = ImageDraw.Draw(layer)
    d.polygon([(x_top - width_top / 2, -20), (x_top + width_top / 2, -20),
               (x_bot + width_bot / 2, h + 20), (x_bot - width_bot / 2, h + 20)],
              fill=int(255 * amp))
    layer = layer.filter(ImageFilter.GaussianBlur(w * 0.045))
    tint = Image.new("RGB", size, color)
    return ImageChops.multiply(tint, Image.merge("RGB", (layer, layer, layer)))


def dust_layer(size, n, rgba=False, color=CHALK):
    """Chalk dust motes at mixed depths."""
    w, h = size
    mode = "RGBA" if rgba else "RGB"
    img = Image.new(mode, size, (0, 0, 0, 0) if rgba else (0, 0, 0))
    near = Image.new(mode, size, (0, 0, 0, 0) if rgba else (0, 0, 0))
    dfar = ImageDraw.Draw(img)
    dnear = ImageDraw.Draw(near)
    for _ in range(n):
        x, y = random.uniform(0, w), random.uniform(0, h)
        depth = random.random()
        r = 0.6 + depth * 2.6
        a = random.uniform(0.25, 1.0) * (0.35 + 0.65 * depth)
        c = (*color, int(255 * a)) if rgba else tuple(int(v * a) for v in color)
        target = dnear if depth > 0.72 else dfar
        target.ellipse([x - r, y - r, x + r, y + r], fill=c)
    img = img.filter(ImageFilter.GaussianBlur(1.6))
    near = near.filter(ImageFilter.GaussianBlur(0.6))
    if rgba:
        img.alpha_composite(near)
        return img
    return ImageChops.add(img, near)


def vignette(img, strength=0.55):
    w, h = img.size
    mask = Image.new("L", (w // 4, h // 4), 0)
    px = mask.load()
    for y in range(mask.height):
        for x in range(mask.width):
            u = x / mask.width - 0.5
            v = y / mask.height - 0.5
            d = math.hypot(u * 1.55, v * 1.3)
            px[x, y] = int(255 * min(1.0, max(0.0, 1.0 - d * strength * 1.8)))
    mask = mask.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
    black = Image.new("RGB", (w, h), (2, 2, 3))
    return Image.composite(img, black, mask)


def iron_hero():
    """Hero backdrop: brushed iron, hard top light, chalk dust, aura accent."""
    w, h = 1200, 750
    img = Image.new("RGB", (w, h), IRON)
    img = apply_centered_overlay(img, streak_texture((w, h), strength=26))
    # hard key light: tight bright shafts from upper right, like gym skylights
    img = ImageChops.add(img, light_shaft((w, h), w * 0.70, w * 0.045, w * 0.55, w * 0.34, (62, 66, 74), 1.0))
    img = ImageChops.add(img, light_shaft((w, h), w * 0.79, w * 0.030, w * 0.70, w * 0.20, (78, 82, 90), 0.85))
    img = ImageChops.add(img, light_shaft((w, h), w * 0.60, w * 0.022, w * 0.42, w * 0.16, (48, 52, 60), 0.7))
    # floor catch-light: hard horizontal platform edge low in frame
    floor = Image.new("L", (w, h), 0)
    fd = ImageDraw.Draw(floor)
    fd.rectangle([0, int(h * 0.845), w, int(h * 0.852)], fill=70)
    floor = floor.filter(ImageFilter.GaussianBlur(2.5))
    img = ImageChops.add(img, ImageChops.multiply(
        Image.new("RGB", (w, h), (150, 165, 190)),
        Image.merge("RGB", (floor, floor, floor))))
    # aura accent: restrained rim glow where the lifter stands + ember bounce
    img = ImageChops.add(img, radial_glow((w, h), w * 0.70, h * 0.66, w * 0.26, BLUE, 0.20))
    img = ImageChops.add(img, radial_glow((w, h), w * 0.71, h * 0.62, w * 0.09, (185, 212, 255), 0.26, power=2.0))
    img = ImageChops.add(img, radial_glow((w, h), w * 0.14, h * 1.04, w * 0.26, EMBER, 0.12))
    img = ImageChops.add(img, dust_layer((w, h), 700))
    img = vignette(img, strength=0.62)
    img = img.resize((2400, 1500), Image.LANCZOS)
    save_webp(img, "iron-hero.webp", quality=80)
    save_webp(img.crop((1150, 0, 2150, 1500)).resize((800, 1200), Image.LANCZOS),
              "iron-hero-mobile.webp", quality=78)


def dust_sprite():
    """Transparent dust field for a parallax layer."""
    img = dust_layer((1600, 1000), 360, rgba=True)
    save_webp(img, "dust.webp", quality=80)


# ---------------------------------------------------------------- lifter ---

def _sample_segment(p0, p1, n, jitter):
    pts = []
    for _ in range(n):
        t = random.random()
        x = p0[0] + (p1[0] - p0[0]) * t + random.gauss(0, jitter)
        y = p0[1] + (p1[1] - p0[1]) * t + random.gauss(0, jitter)
        pts.append((x, y))
    return pts


def _sample_circle(c, r, n, jitter, arc=(0, 6.2832)):
    pts = []
    for _ in range(n):
        a = random.uniform(*arc)
        rr = r + random.gauss(0, jitter)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    return pts


def lifter():
    """Chalk-particle lifter at overhead lockout — front view, arms in a V,
    loaded bar overhead with big visible plates. The most iconic strength
    silhouette there is; particles add the chalk/aura treatment."""
    S = 1000
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    def P(x, y):
        return (x * S, y * S)

    bar_y = 0.175
    pts = []
    # ---- barbell: long straight bar + two plates with hubs
    pts += _sample_segment(P(0.13, bar_y), P(0.87, bar_y), 700, 0.0045 * S)
    for px_ in (0.205, 0.795):
        pts += _sample_circle(P(px_, bar_y), 0.082 * S, 800, 0.0045 * S)
        pts += _sample_circle(P(px_, bar_y), 0.060 * S, 260, 0.004 * S)
        pts += _sample_circle(P(px_, bar_y), 0.024 * S, 200, 0.0035 * S)
    # collar plates (smaller, just inside)
    for px_ in (0.285, 0.715):
        pts += _sample_circle(P(px_, bar_y), 0.046 * S, 320, 0.004 * S)

    # ---- figure: front view, arms up in a V to the bar
    head_c, head_r = P(0.500, 0.335), 0.040 * S
    segs = [
        # arms: shoulder -> hand (on the bar)
        (P(0.462, 0.435), P(0.408, bar_y + 0.015), 460, 0.0135 * S),
        (P(0.538, 0.435), P(0.592, bar_y + 0.015), 460, 0.0135 * S),
        # shoulder girdle
        (P(0.455, 0.440), P(0.545, 0.440), 260, 0.014 * S),
        # torso: shoulders taper to hips
        (P(0.478, 0.450), P(0.484, 0.620), 520, 0.026 * S),
        (P(0.522, 0.450), P(0.516, 0.620), 520, 0.026 * S),
        # hips
        (P(0.478, 0.625), P(0.522, 0.625), 200, 0.014 * S),
        # legs: slight A-stance
        (P(0.483, 0.635), P(0.452, 0.790), 420, 0.0185 * S),
        (P(0.517, 0.635), P(0.548, 0.790), 420, 0.0185 * S),
        (P(0.452, 0.790), P(0.438, 0.935), 340, 0.0140 * S),
        (P(0.548, 0.790), P(0.562, 0.935), 340, 0.0140 * S),
        # feet
        (P(0.418, 0.945), P(0.462, 0.945), 130, 0.007 * S),
        (P(0.538, 0.945), P(0.582, 0.945), 130, 0.007 * S),
    ]
    for p0, p1, n, j in segs:
        pts += _sample_segment(p0, p1, n, j)
    pts += _sample_circle(head_c, head_r, 240, 0.007 * S)
    pts += [(head_c[0] + random.gauss(0, head_r * 0.5),
             head_c[1] + random.gauss(0, head_r * 0.5)) for _ in range(180)]

    # ---- depth: aura halo behind, chalk particles in front
    halo = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    for x, y in pts:
        if random.random() < 0.5:
            r = random.uniform(3.5, 7.5)
            hd.ellipse([x - r, y - r, x + r, y + r], fill=(*BLUE, 30))
    halo = halo.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(halo)

    for x, y in pts:
        r = random.uniform(0.8, 2.2)
        c = CHALK if random.random() < 0.78 else BLUE
        a = random.randint(130, 245)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(*c, a))

    # chalk puffs drifting off the hands
    puff = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pd = ImageDraw.Draw(puff)
    for hx in (0.408, 0.592):
        hc = P(hx, bar_y + 0.02)
        for _ in range(170):
            a = random.uniform(0, 6.2832)
            rr = abs(random.gauss(0, 0.05 * S)) + 0.012 * S
            x, y = hc[0] + rr * math.cos(a), hc[1] + rr * math.sin(a) * 0.8
            r = random.uniform(0.5, 1.5)
            pd.ellipse([x - r, y - r, x + r, y + r], fill=(*CHALK, random.randint(18, 70)))
    img.alpha_composite(puff.filter(ImageFilter.GaussianBlur(1.1)))

    save_webp(img, "lifter.webp", quality=82)


# ------------------------------------------------------------- data viz ---

def load_curve():
    """Training-load data art: weekly bars + glowing trend line, alpha bg."""
    w, h = 1400, 520
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = 70
    n = 16
    bw = (w - pad * 2) / n
    random.seed(23)
    # synthetic block: three rising waves with a deload dip
    loads = []
    for i in range(n):
        block = i // 4
        step = i % 4
        base = 0.35 + block * 0.13
        v = base + step * 0.07 if step < 3 else base - 0.10
        loads.append(min(1.0, v + random.uniform(-0.02, 0.02)))
    # bars
    for i, v in enumerate(loads):
        x0 = pad + i * bw + bw * 0.22
        x1 = pad + (i + 1) * bw - bw * 0.22
        y0 = h - 60 - v * (h - 150)
        deload = (i % 4) == 3
        if deload:
            # hollow chalk outline marks the deload week, on-palette
            d.rounded_rectangle([x0, y0, x1, h - 60], radius=4,
                                outline=(*CHALK, 120), width=2)
        else:
            d.rounded_rectangle([x0, y0, x1, h - 60], radius=4, fill=(*CHALK, 38))
    # glow trend line through bar tops
    tops = [(pad + (i + 0.5) * bw, h - 60 - v * (h - 150)) for i, v in enumerate(loads)]
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line(tops, fill=(*BLUE, 255), width=5, joint="curve")
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(7)))
    d.line(tops, fill=(210, 228, 255, 255), width=3, joint="curve")
    for x, y in tops:
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(240, 247, 255, 255))
    # baseline + tick marks
    d.line([(pad - 10, h - 60), (w - pad + 10, h - 60)], fill=(*CHALK, 60), width=2)
    for i in range(0, n + 1, 4):
        x = pad + i * bw
        d.line([(x, h - 60), (x, h - 48)], fill=(*CHALK, 90), width=2)
    save_webp(img, "load-curve.webp", quality=85)


def waveform():
    """Recovery waveform strip, alpha bg — sleep/readiness pulse."""
    w, h = 1600, 240
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    random.seed(31)
    pts = []
    for x in range(0, w, 4):
        u = x / w
        env = math.sin(u * math.pi) ** 0.5
        v = (math.sin(u * 40) * 0.35 + math.sin(u * 9 + 1.4) * 0.45 +
             random.uniform(-0.12, 0.12)) * env
        pts.append((x, h / 2 + v * h * 0.42))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line(pts, fill=(*TEAL, 255), width=4)
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(6)))
    d.line(pts, fill=(205, 248, 232, 255), width=2)
    save_webp(img, "waveform.webp", quality=85)


# -------------------------------------------------------------- og card ---

def og_card():
    """1200x630 social card on the iron backdrop."""
    src = Image.open(os.path.join(OUT, "iron-hero.webp")).convert("RGB")
    img = src.resize((1200, 750), Image.LANCZOS).crop((0, 60, 1200, 690))
    d = ImageDraw.Draw(img)
    f_kick = ImageFont.truetype(FONT_MED, 30)
    f_big = ImageFont.truetype(FONT_BOLD, 132)
    f_aura = ImageFont.truetype(FONT_SERIF_IT, 150)
    f_sub = ImageFont.truetype(FONT_MED, 33)
    # mark
    try:
        mark = Image.open(os.path.join(OUT, "..", "ora-mark-transparent.png")).convert("RGBA")
        mark = mark.resize((84, 84), Image.LANCZOS)
        img.paste(mark, (76, 64), mark)
        d.text((176, 86), "ORA", font=ImageFont.truetype(FONT_BOLD, 44), fill=CHALK)
    except Exception:
        d.text((76, 70), "ORA", font=ImageFont.truetype(FONT_BOLD, 56), fill=CHALK)
    d.text((78, 212), "PRIVATE BETA — AI COACHING FOR SERIOUS LIFTERS",
           font=f_kick, fill=(170, 176, 188))
    d.text((72, 268), "Grow your", font=f_big, fill=CHALK)
    # gradient "Aura." via per-letter fill
    x = 78
    word = "Aura."
    for i, ch in enumerate(word):
        t = i / max(1, len(word) - 1)
        col = tuple(int(BLUE[j] + (TEAL[j] - BLUE[j]) * t) for j in range(3))
        d.text((x, 398), ch, font=f_aura, fill=col)
        x += d.textlength(ch, font=f_aura)
    d.text((78, 562), "oracoach.app", font=f_sub, fill=(150, 156, 170))
    path = os.path.join(OUT, "og-card.png")
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path} ({os.path.getsize(path)//1024} KB)")


if __name__ == "__main__":
    iron_hero()
    dust_sprite()
    lifter()
    load_curve()
    waveform()
    og_card()
    print("done")
