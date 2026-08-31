#!/usr/bin/env python3
"""Render 4 bilingual 1920x1080 SkillSynth title cards with pure PIL.

Cards: welcome, section-discover, section-admin, close. Warm Craft brand:
paper/ochre/sage, 1px hairlines, flat, no gradients. Output written to
brand/video/work/frames/ resolved from the repo root (via the BRAND env var
or this file's ancestry), so the script works from any cwd.
"""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat

W, H = 1920, 1080
MARGIN = 64

PAPER = "#FBF6EC"
INK = "#2A2521"
INK_SOFT = "#4A4238"
OCHRE_DEEP = "#8A6520"
LINE = "#E4DAC8"

FONTS = {
    "bricolage": "/home/zuhair/.local/share/fonts/BricolageGrotesque.ttf",
    "messiri": "/home/zuhair/.local/share/fonts/ElMessiri.ttf",
    "public": "/home/zuhair/.local/share/fonts/PublicSans.ttf",
    "noto_ar": "/usr/share/fonts/noto/NotoSansArabic-Regular.ttf",
}

MARK_REL = "brand/identity/logo/mark-only.png"

AR_WELCOME = "منصة تعلّم تُكيّف مسارك لك"
AR_DISCOVER = "اكتشف · تعلّم · انمُ"
AR_ADMIN = "الأدوات الإدارية"
AR_CLOSE = "مسار من ما تعرفه إلى ما يمكنك أن تصبح"
EN_WELCOME_SUB = "An adaptive learning path, built around you"
EN_CLOSE_LOG = "A journey from what you know to what you could become."


def repo_root():
    """Return the repo root from the BRAND env var or this file's ancestry."""
    env = os.environ.get("BRAND")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[3]


def load_font(face, size):
    """Return a PIL font for the named face at the given pixel size."""
    return ImageFont.truetype(FONTS[face], size)


def base_image():
    """Return a paper background with a 1px hairline frame inset MARGIN."""
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle(
        [MARGIN, MARGIN, W - MARGIN, H - MARGIN], outline=LINE, width=1
    )
    return im


def draw_wordmark(draw, cx, y, font_size=96):
    """Draw the two-tone 'SkillSynth' wordmark centered at (cx, middle-y)."""
    f = load_font("bricolage", font_size)
    w_skill = f.getlength("Skill")
    total = w_skill + f.getlength("Synth")
    left = cx - total / 2
    draw.text((left, y), "Skill", font=f, fill=INK, anchor="lm")
    draw.text((left + w_skill, y), "Synth", font=f, fill=OCHRE_DEEP, anchor="lm")


def draw_mixed_ar(draw, runs, cx, y, font_size=56, lang="ar"):
    """Draw RTL runs (text,color) as one centered line, rightmost run first.

    First logical run renders rightmost; each run placed via right-edge
    anchoring so the whole line reads right-to-left with mixed colors.
    """
    f = load_font("messiri", font_size)
    widths = [f.getlength(t, direction="rtl", language=lang) for t, _ in runs]
    total = sum(widths)
    right = cx + total / 2
    cur = 0
    for (t, c), wd in zip(runs, widths):
        draw.text((right - cur, y), t, font=f, fill=c, direction="rtl",
                  language=lang, anchor="rm")
        cur += wd


def draw_center(draw, text, face, size, cx, y, fill, direction="ltr"):
    """Draw a single centered line at (cx, middle-y) and return its width."""
    f = load_font(face, size)
    w = f.getlength(text, direction=direction, language="ar" if direction == "rtl" else "ltr")
    draw.text((cx, y), text, font=f, fill=fill, direction=direction,
              language="ar" if direction == "rtl" else "ltr", anchor="mm")
    return w


def paste_mark(im, cx, cy, size=180):
    """Paste the 1:1 logo mark centered at (cx, cy), preserving aspect."""
    src = Image.open(repo_root() / MARK_REL)
    mark = src.resize((size, size), Image.LANCZOS)
    im.paste(mark, (int(cx - size / 2), int(cy - size / 2)), mark)


def build_welcome(root):
    """Build the welcome title card (mark, wordmark, Arabic tagline, subline)."""
    im = base_image()
    d = ImageDraw.Draw(im)
    paste_mark(im, W / 2, 235, 180)
    draw_wordmark(d, W / 2, 465, 96)
    draw_mixed_ar(d, [("منصة تعلّم تُكيّف ", INK), ("مسارك", OCHRE_DEEP),
                      (" لك", INK)], W / 2, 625, 56)
    d.text((W / 2, 760), EN_WELCOME_SUB, font=load_font("public", 30),
           fill=INK_SOFT, anchor="mm")
    return im


def build_discover(root):
    """Build the 'Discover · Learn · Grow' section card."""
    im = base_image()
    d = ImageDraw.Draw(im)
    paste_mark(im, W / 2, 250, 160)
    d.text((W / 2, 560), "Discover · Learn · Grow", font=load_font("bricolage", 72),
           fill=INK, anchor="mm")
    draw_center(d, AR_DISCOVER, "messiri", 48, W / 2, 700, OCHRE_DEEP, "rtl")
    return im


def build_admin(root):
    """Build the 'Admin tools' section card."""
    im = base_image()
    d = ImageDraw.Draw(im)
    paste_mark(im, W / 2, 250, 160)
    d.text((W / 2, 560), "Admin tools", font=load_font("bricolage", 72),
           fill=INK, anchor="mm")
    draw_center(d, AR_ADMIN, "messiri", 48, W / 2, 700, OCHRE_DEEP, "rtl")
    return im


def build_close(root):
    """Build the closing card (mark, wordmark, Arabic accent, logline)."""
    im = base_image()
    d = ImageDraw.Draw(im)
    paste_mark(im, W / 2, 235, 180)
    draw_wordmark(d, W / 2, 465, 96)
    d.text((W / 2, 625), AR_CLOSE, font=load_font("messiri", 56),
           fill=OCHRE_DEEP, direction="rtl", language="ar", anchor="mm")
    d.text((W / 2, 760), EN_CLOSE_LOG, font=load_font("public", 30),
           fill=INK_SOFT, anchor="mm")
    return im


BUILDERS = [
    ("welcome.png", build_welcome),
    ("section-discover.png", build_discover),
    ("section-admin.png", build_admin),
    ("close.png", build_close),
]


def cmap_coverage(font_path, text):
    """Return a list of codepoints in text missing from the font's cmap."""
    from fontTools.ttLib import TTFont
    cmap = TTFont(font_path).getBestCmap()
    return [hex(ord(c)) for c in text if ord(c) not in cmap]


def verify_image(path):
    """Assert dims and non-blank stats; return (dims, mean, std, palette count)."""
    im = Image.open(path)
    assert im.size == (W, H), f"{path.name} wrong size {im.size}"
    st = ImageStat.Stat(im.convert("RGB"))
    colors = len(im.convert("RGB").getcolors(2 ** 24) or [])
    return (im.size,
            tuple(round(v, 2) for v in st.mean),
            tuple(round(v, 2) for v in st.stddev),
            colors)


def render_all(root):
    """Render every card to the frames dir and return the output paths."""
    out = root / "brand/video/work/frames"
    out.mkdir(parents=True, exist_ok=True)
    for name, builder in BUILDERS:
        im = builder(root)
        im.save(out / name)
    return out


def verify_all(root, out):
    """Run dims, cmap, non-blank, and mixed-line checks; print a listing."""
    from fontTools import ttLib  # noqa: F401

    checks = [
        (AR_WELCOME, FONTS["messiri"]),
        (AR_DISCOVER, FONTS["messiri"]),
        (AR_ADMIN, FONTS["messiri"]),
        (AR_CLOSE, FONTS["messiri"]),
        ("SkillSynth", FONTS["bricolage"]),
        ("Discover · Learn · Grow", FONTS["bricolage"]),
        ("Admin tools", FONTS["bricolage"]),
        (EN_WELCOME_SUB, FONTS["public"]),
        (EN_CLOSE_LOG, FONTS["public"]),
    ]
    for text, font in checks:
        missing = cmap_coverage(font, text)
        status = "OK" if not missing else f"MISSING {missing}"
        print(f"cmap  {status:16} {Path(font).name:28} {text!r}")

    for name, _ in BUILDERS:
        p = out / name
        dims, mean, std, colors = verify_image(p)
        print(f"image {p.name:22} dims={dims[0]}x{dims[1]} "
              f"mean={mean} std={std} colors={colors}")
    print_verify_mixed_line()


def mixed_line_assert():
    """Compare per-run RTL mask to a single-run reference; assert within tol."""
    f = load_font("messiri", 56)
    ref = Image.new("L", (1600, 140), 0)
    ImageDraw.Draw(ref).text((1000, 70), AR_WELCOME, font=f, fill=255,
                             direction="rtl", language="ar", anchor="rm")
    mx = Image.new("L", (1600, 140), 0)
    dm = ImageDraw.Draw(mx)
    runs = [("منصة تعلّم تُكيّف ", INK), ("مسارك", OCHRE_DEEP), (" لك", INK)]
    widths = [f.getlength(t, direction="rtl", language="ar") for t, _ in runs]
    right = 1000
    cur = 0
    for (t, _), wd in zip(runs, widths):
        dm.text((right - cur, 70), t, font=f, fill=255,
                direction="rtl", language="ar", anchor="rm")
        cur += wd
    rb = ref.getbbox()
    mb = mx.getbbox()
    assert rb and mb, "empty RTL mask"
    dx = abs(rb[0] - mb[0])
    dy = abs(rb[3] - mb[3])
    print(f"rtl-mask mixed-vs-reference bbox delta=({dx},{dy}) "
          f"(within 4px) -> {'OK' if dx <= 4 and dy <= 4 else 'FAIL'}")
    assert dx <= 4 and dy <= 4, f"RTL mixed line drifted ({dx},{dy})"


def print_verify_mixed_line():
    """Run and report the mixed-color RTL line self-verification."""
    mixed_line_assert()


def main():
    """Render all cards, verify them, and print the frames directory listing."""
    root = repo_root()
    out = render_all(root)
    verify_all(root, out)
    print("\n" + "-" * 60)
    print("brand/video/work/frames/")
    for p in sorted(out.glob("*.png")):
        print(f"  {p.name}  {p.stat().st_size} bytes")


if __name__ == "__main__":
    main()
