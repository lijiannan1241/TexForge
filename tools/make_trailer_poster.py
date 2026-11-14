# -*- coding: utf-8 -*-
"""生成预告片海报（首页封面与视频 poster 共用）。

输出：assets/video/trailer-zh-poster.jpg、trailer-en-poster.jpg（1920x1080）。
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ICON = ROOT / "assets/img/icon-1024.png"
OUT = ROOT / "assets/video"
W, H = 1920, 1080

LIGHT = (232, 240, 248)
SUB = (150, 170, 190)
TEAL = (34, 211, 238)
AMBER = (251, 191, 36)

TEXT = {
    "zh": ("统一图像批处理与纹理图集打包", "113 批处理动作 · 69 图集格式 · 24 引擎格式", "44 秒演示"),
    "en": ("Batch image processing & texture atlas packing",
           "113 batch actions · 69 atlas formats · 24 engine formats", "44 second demo"),
}


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    names = ["msyhbd.ttc", "seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"] if bold \
        else ["msyh.ttc", "segoeui.ttf", "arial.ttf"]
    for n in names:
        p = Path("C:/Windows/Fonts") / n
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except OSError:
                continue
    return ImageFont.load_default()


def fit(text: str, max_w: int, start: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    s = start
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    while s > 12:
        f = font(s, bold)
        if probe.textbbox((0, 0), text, font=f)[2] <= max_w:
            return f
        s -= 2
    return font(12, bold)


def base() -> Image.Image:
    img = Image.new("RGB", (W, H), (8, 14, 22))
    d = ImageDraw.Draw(img)
    top, bot = (14, 26, 40), (6, 11, 18)
    for y in range(H):
        k = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(round(top[i] + (bot[i] - top[i]) * k) for i in range(3)))
    # 网格
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, W, 64):
        gd.line([(x, 0), (x, H)], fill=(255, 255, 255, 10), width=1)
    for y in range(0, H, 64):
        gd.line([(0, y), (W, y)], fill=(255, 255, 255, 10), width=1)
    img = Image.alpha_composite(img.convert("RGBA"), grid)
    # 光晕
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([int(W * .5), int(-H * .35), int(W * 1.28), int(H * .8)],
                                 fill=(34, 211, 238, 46))
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    img = Image.alpha_composite(img, glow)
    warm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(warm).ellipse([int(-W * .22), int(H * .55), int(W * .42), int(H * 1.3)],
                                 fill=(251, 191, 36, 30))
    warm = warm.filter(ImageFilter.GaussianBlur(150))
    return Image.alpha_composite(img, warm).convert("RGB")


def compose(lang: str) -> Image.Image:
    img = base()
    tag, stats, badge = TEXT[lang]

    icon = Image.open(ICON).convert("RGBA")
    size = 360
    icon = icon.resize((size, size), Image.LANCZOS)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.paste(icon, (int(W / 2 - size / 2), 190), icon)
    shadow = shadow.filter(ImageFilter.GaussianBlur(38))
    img = Image.alpha_composite(img.convert("RGBA"), shadow)
    img.paste(icon, (int(W / 2 - size / 2), 180), icon)

    d = ImageDraw.Draw(img)
    name_f = font(126)
    tw = d.textbbox((0, 0), "TexForge", font=name_f)[2]
    d.text(((W - tw) / 2, 590), "TexForge", font=name_f, fill=LIGHT)

    for i, (txt, f, color, y) in enumerate((
        (tag, fit(tag, int(W * .78), 52, False), SUB, 760),
        (stats, fit(stats, int(W * .7), 34, False), TEAL, 840),
    )):
        w = d.textbbox((0, 0), txt, font=f)[2]
        d.text(((W - w) / 2, y), txt, font=f, fill=color)

    pf = font(34)
    tw = d.textbbox((0, 0), badge, font=pf)[2]
    pad = 30
    tri_w, tri_h, gap = 20, 24, 14
    total = pad + tri_w + gap + tw + pad
    x0, y0 = (W - total) / 2, 918
    d.rounded_rectangle([x0, y0, x0 + total, y0 + 78], radius=39, fill=(34, 211, 238, 255))
    cx = x0 + pad
    cy = y0 + 39
    d.polygon([(cx, cy - tri_h / 2), (cx, cy + tri_h / 2), (cx + tri_w, cy)],
              fill=(5, 32, 43))
    d.text((cx + tri_w + gap, y0 + 20), badge, font=pf, fill=(5, 32, 43))
    return img.convert("RGB")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in ("zh", "en"):
        p = OUT / f"trailer-{lang}-poster.jpg"
        compose(lang).save(p, "JPEG", quality=88, optimize=True)
        print("wrote", p.relative_to(ROOT), f"{p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
