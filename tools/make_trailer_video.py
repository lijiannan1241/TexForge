# -*- coding: utf-8 -*-
"""生成预告片 MP4（1920x1080 / 30fps / 44s）与配套 VTT 字幕。

素材：真实界面截图（中英各 4 个工作区）+ 品牌卡片。
构图：截图缩放进 1600x900 圆角卡片（含阴影），底部细信息条放章节标题，
     全程 Ken Burns 轻微推近 + 交叉溶解；原始 RGB 帧经管道交给 ffmpeg 编码。

输出：
  assets/video/trailer-zh.mp4 / trailer-en.mp4
  assets/video/trailer-zh.vtt / trailer-en.vtt

用法：python tools/make_trailer_video.py [--lang zh|en|both]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import site_content as C  # noqa: E402
from make_trailer_poster import base, fit, font  # noqa: E402

W, H, FPS = 1920, 1080, 30
FADE = 0.55                      # 交叉溶解时长（秒）
SHOT_ROUND = 14                  # 卡片圆角

CARD_W, CARD_H = 1600, 900       # 16:9，与截图一致，缩放不变形
CARD_X, CARD_Y = (W - CARD_W) // 2, 28
BAR_Y = 952                      # 底部信息条顶边

SCREEN_SRC = Path("D:/其他/convert_images/store/screenshots")
OUT = ROOT / "assets/video"

LIGHT = (232, 240, 248)
SUB = (148, 168, 188)
TEAL = (34, 211, 238)
AMBER = (251, 191, 36)


def mono(size: int):
    for n in ("consola.ttf", "cour.ttf", "arial.ttf"):
        p = Path("C:/Windows/Fonts") / n
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except OSError:
                continue
    return font(size, False)


# ---------------------------------------------------------------- 卡片底板
def stage(content: Image.Image | None = None, terminal: list | None = None) -> Image.Image:
    """品牌渐变底 + 1600x900 圆角卡片（截图或终端内容）。"""
    img = base().convert("RGBA")
    x0, y0, x1, y1 = CARD_X, CARD_Y, CARD_X + CARD_W, CARD_Y + CARD_H

    # 投影
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([x0 + 6, y0 + 22, x1 + 6, y1 + 22],
                                        radius=SHOT_ROUND, fill=(0, 0, 0, 170))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(30)))

    # 圆角遮罩后的内容
    card = Image.new("RGBA", (CARD_W, CARD_H), (9, 16, 25, 255))
    if content is not None:
        card.paste(content.convert("RGB").resize((CARD_W, CARD_H), Image.LANCZOS), (0, 0))
    if terminal is not None:
        _draw_terminal(card, terminal)

    mask = Image.new("L", (CARD_W, CARD_H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, CARD_W - 1, CARD_H - 1], radius=SHOT_ROUND, fill=255)
    img.paste(card, (x0, y0), mask)

    # 细边框
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0, y0, x1, y1], radius=SHOT_ROUND, outline=(255, 255, 255, 46), width=2)
    return img.convert("RGB")


def _draw_terminal(card: Image.Image, lines: list) -> None:
    """在卡片内画终端窗口。"""
    d = ImageDraw.Draw(card)
    top = 74
    d.rectangle([0, top, CARD_W, CARD_H], fill=(9, 16, 25, 255))
    d.rectangle([0, top, CARD_W, top + 54], fill=(22, 34, 48, 255))
    for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        d.ellipse([28 + i * 28, top + 20, 42 + i * 28, top + 34], fill=c)
    d.text((128, top + 14), lines[0][0], font=mono(26), fill=(150, 170, 190))

    f = mono(30)
    y = top + 100
    for text, kind in lines[1:]:
        color = {"cmd": TEAL, "ok": (110, 231, 183), "out": AMBER,
                 "dim": (116, 134, 154)}[kind]
        d.text((52, y), text, font=f, fill=color)
        y += 54


CLI_LINES = {
    "zh": [
        ("texforge-cli - preset: pixel-ui.json", None),
        ("$ texforge-cli --preset pixel-ui.json --in ./raw --out ./build", "cmd"),
        ("[  1/128] hero_01.png      resize 512x512      ok", "dim"),
        ("[  2/128] hero_02.png      trim + padding      ok", "dim"),
        ("[  3/128] portrait_01.png  normal from height  ok", "dim"),
        ("[ 64/128] icon_set/*.png   ORM pack            ok", "dim"),
        ("[128/128] ui_sheet.png     atlas 2048x2048     ok", "ok"),
        ("", "dim"),
        ("→ build/atlas.png          2048 x 2048   POT", "out"),
        ("→ build/atlas.json         unity  descriptor", "out"),
        ("→ build/report.csv         128 ok / 0 failed", "out"),
        ("", "dim"),
        ("done in 6.4s - exit code 0", "ok"),
    ],
    "en": [
        ("texforge-cli - preset: pixel-ui.json", None),
        ("$ texforge-cli --preset pixel-ui.json --in ./raw --out ./build", "cmd"),
        ("[  1/128] hero_01.png      resize 512x512      ok", "dim"),
        ("[  2/128] hero_02.png      trim + padding      ok", "dim"),
        ("[  3/128] portrait_01.png  normal from height  ok", "dim"),
        ("[ 64/128] icon_set/*.png   ORM pack            ok", "dim"),
        ("[128/128] ui_sheet.png     atlas 2048x2048     ok", "ok"),
        ("", "dim"),
        ("-> build/atlas.png         2048 x 2048   POT", "out"),
        ("-> build/atlas.json        unity  descriptor", "out"),
        ("-> build/report.csv        128 ok / 0 failed", "out"),
        ("", "dim"),
        ("done in 6.4s - exit code 0", "ok"),
    ],
}


def end_card(lang: str) -> Image.Image:
    """结尾卡：图标 + 产品名 + 商店入口。"""
    img = base().convert("RGBA")
    icon = Image.open(ROOT / "assets/img/icon-1024.png").convert("RGBA")
    size = 300
    icon = icon.resize((size, size), Image.LANCZOS)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.paste(icon, (W // 2 - size // 2, 168), icon)
    sh = sh.filter(ImageFilter.GaussianBlur(34))
    img = Image.alpha_composite(img, sh)
    img.paste(icon, (W // 2 - size // 2, 160), icon)

    d = ImageDraw.Draw(img)
    nf = font(112)
    tw = d.textbbox((0, 0), "TexForge", font=nf)[2]
    d.text(((W - tw) / 2, 512), "TexForge", font=nf, fill=LIGHT)

    sub = ("Windows 10 / 11 · 从 Microsoft Store 安装"
           if lang == "zh" else "Windows 10 / 11 · Install from Microsoft Store")
    sf = fit(sub, int(W * .8), 44, False)
    sw = d.textbbox((0, 0), sub, font=sf)[2]
    d.text(((W - sw) / 2, 668), sub, font=sf, fill=SUB)

    pill_txt = "Microsoft Store" if lang == "zh" else "Get it on Microsoft Store"
    pf = font(36)
    pw = d.textbbox((0, 0), pill_txt, font=pf)[2]
    pad, gap, iw = 34, 16, 29
    total = pad + iw + gap + pw + pad
    x0, y0 = (W - total) / 2, 800
    d.rounded_rectangle([x0, y0, x0 + total, y0 + 88], radius=44, fill=TEAL)
    # 微软四方格标（与文字同色，避免图标在青底上糊成一团）
    sq, sp = 13, 3
    gx, gy = int(x0 + pad), int(y0 + (88 - (sq * 2 + sp)) / 2)
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        gx2 = gx + dx * (sq + sp)
        gy2 = gy + dy * (sq + sp)
        d.rectangle([gx2, gy2, gx2 + sq, gy2 + sq], fill=(5, 32, 43))
    d.text((x0 + pad + iw + gap, y0 + 22), pill_txt, font=pf, fill=(5, 32, 43))
    return img.convert("RGB")


# ---------------------------------------------------------------- 场景
def build_scenes(lang: str):
    """[(start, end, image, label, desc, kind)]  kind: intro|shot|cli|end"""
    ch = C.TRAILER[lang]["chapters"]
    total = 44.0
    ends = [c[0] for c in ch[1:]] + [total]

    zh_shots = ["zh_CN_tab1.png", "zh_CN_tab3.png", "zh_CN_tab0.png", "zh_CN_tab2.png"]
    en_shots = ["en_tab1.png", "en_tab3.png", "en_tab0.png", "en_tab2.png"]
    srcs = zh_shots if lang == "zh" else en_shots

    scenes = [(ch[0][0], ends[0],
               Image.open(OUT / f"trailer-{lang}-poster.jpg").convert("RGB"),
               ch[0][1], ch[0][2], "intro")]
    for i in range(4):
        shot = Image.open(SCREEN_SRC / srcs[i]).convert("RGB")
        scenes.append((ch[i + 1][0], ends[i + 1], stage(content=shot),
                       ch[i + 1][1], ch[i + 1][2], "shot"))
    scenes.append((ch[5][0], ends[5], stage(terminal=CLI_LINES[lang]),
                   ch[5][1], ch[5][2], "cli"))
    scenes.append((ch[6][0], total, end_card(lang), ch[6][1], ch[6][2], "end"))
    return scenes


# ---------------------------------------------------------------- 底部信息条
def info_bar(idx: int, total: int, label: str, desc: str, accent) -> tuple[Image.Image, tuple[int, int]]:
    """细信息条：序号 · 标题 · 说明（单行），只覆盖底部留白区。"""
    x, y = 96, BAR_Y
    num = f"{idx:02d} / {total:02d}"
    nf, lf, df = font(24, True), font(44, True), font(30, False)

    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    nw = probe.textbbox((0, 0), num, font=nf)[2]
    lw = probe.textbbox((0, 0), label, font=lf)[2]
    dw = probe.textbbox((0, 0), desc, font=df)[2]
    max_w = W - x * 2 - 40

    # 太长就压缩说明字号
    while nw + lw + dw + 150 > max_w and df.size > 20:
        df = font(df.size - 2, False)
        dw = probe.textbbox((0, 0), desc, font=df)[2]

    gap1, gap2 = 30, 34
    bar_w = 6
    w = bar_w + 24 + nw + gap1 + lw + gap2 + dw + 8
    h = 96

    panel = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rectangle([0, 10, bar_w, h - 10], fill=accent + (255,))
    pd.text((bar_w + 24, 30), num, font=nf, fill=accent)
    pd.text((bar_w + 24 + nw + gap1, 14), label, font=lf, fill=LIGHT)
    pd.text((bar_w + 24 + nw + gap1 + lw + gap2, 26), desc, font=df, fill=SUB)
    return panel, (x, y)


def watermark() -> tuple[Image.Image, tuple[int, int]]:
    txt = "TexForge"
    f = font(26, True)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tw = probe.textbbox((0, 0), txt, font=f)[2]
    th = probe.textbbox((0, 0), txt, font=f)[3]
    lay = Image.new("RGBA", (tw + 6, th + 8), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((3, 2), txt, font=f, fill=(255, 255, 255, 120))
    return lay, (W - tw - 88, BAR_Y + 34)


# ---------------------------------------------------------------- 逐帧
def render_frame(src: Image.Image, local_t: float, dur: float, kind: str) -> Image.Image:
    frac = min(1.0, max(0.0, local_t / max(dur, 0.001)))
    z = (1.0 + 0.03 * frac) if kind in ("intro", "end") else (1.0 + 0.05 * frac)
    cw, chh = int(W / z), int(H / z)
    cx, cy = (src.width - cw) // 2, (src.height - chh) // 2
    return src.crop((cx, cy, cx + cw, cy + chh)).resize((W, H), Image.BILINEAR)


def _fade_alpha(lay: Image.Image, a: float) -> Image.Image:
    out = lay.copy()
    out.putalpha(out.getchannel("A").point(lambda v: int(v * a)))
    return out


def _ffmpeg() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def make_video(lang: str) -> Path:
    scenes = build_scenes(lang)
    total = scenes[-1][1]
    nframes = int(total * FPS)

    accents = [TEAL, AMBER, TEAL, AMBER, TEAL]
    bars: list = [None] * len(scenes)
    k = 0
    for i, (s, e, img, label, desc, kind) in enumerate(scenes):
        if kind in ("shot", "cli"):
            bars[i] = info_bar(i + 1, len(scenes), label, desc, accents[k % len(accents)])
            k += 1

    wm = watermark()
    out = OUT / f"trailer-{lang}.mp4"
    cmd = [_ffmpeg(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    starts = [s for s, *_ in scenes]
    try:
        for n in range(nframes):
            t = n / FPS
            i = 0
            for k2, st in enumerate(starts):
                if t >= st:
                    i = k2
            s, e, img, label, desc, kind = scenes[i]
            dur = e - s
            frame = render_frame(img, t - s, dur, kind)

            if i + 1 < len(scenes) and t > e - FADE:
                a = (t - (e - FADE)) / FADE
                nxt = scenes[i + 1]
                frame = Image.blend(frame, render_frame(nxt[2], 0.0, nxt[1] - nxt[0], nxt[5]),
                                    min(1.0, max(0.0, a)))

            bar = bars[i]
            if bar is not None:
                panel, pos = bar
                lt = t - s
                alpha = 1.0
                if lt < 0.55:
                    alpha = lt / 0.55
                if lt > dur - 0.45:
                    alpha = max(0.0, (dur - lt) / 0.45)
                if alpha > 0.02:
                    p = panel if alpha >= 0.999 else _fade_alpha(panel, alpha)
                    frame.paste(p, pos, p)
                frame.paste(wm[0], wm[1], wm[0])

            proc.stdin.write(frame.convert("RGB").tobytes())
    finally:
        proc.stdin.close()
        rc = proc.wait()
    if rc != 0:
        raise SystemExit(f"ffmpeg failed rc={rc}")
    print(f"wrote {out.relative_to(ROOT)}  {out.stat().st_size // 1024} KB")
    return out


# ---------------------------------------------------------------- VTT
def _ts(sec: float) -> str:
    return f"{int(sec // 3600):02d}:{int((sec % 3600) // 60):02d}:{sec % 60:06.3f}"


def make_vtt(lang: str) -> Path:
    ch = C.TRAILER[lang]["chapters"]
    ends = [c[0] for c in ch[1:]] + [44.0]
    lines = ["WEBVTT", ""]
    for i, ((sec, label, desc), end) in enumerate(zip(ch, ends), 1):
        lines += [str(i), f"{_ts(sec)} --> {_ts(end)}", f"{label} — {desc}", ""]
    p = OUT / f"trailer-{lang}.vtt"
    p.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {p.relative_to(ROOT)}")
    return p


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="both", choices=["zh", "en", "both"])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in (["zh", "en"] if args.lang == "both" else [args.lang]):
        make_video(lang)
        make_vtt(lang)


if __name__ == "__main__":
    main()
