#!/usr/bin/env python3
"""Rasterize the SkillSynth thesis cover SVGs to 300 dpi PNG previews and vector print PDFs.

Uses rsvg-convert (librsvg). PNGs are previews at 300 dpi (A4 panels ≈2480x3508, jacket media
≈5216x3583); PDFs stay vector. All output stays RGB — convert to CMYK at the print shop only.
Re-run after any change to cover_spec.py / build_covers.py. Run: python3 render.py"""
from __future__ import annotations
import pathlib
import subprocess

DPI = 300
HERE = pathlib.Path(__file__).resolve().parent

PANELS = ("front", "back", "spine")
JACKET = "jacket"
INSIDE = "inside"


def src(kind: str) -> pathlib.Path:
    """Source SVG path for a panel, jacket, or inside sheet. Caller: render.*; callee: none."""
    return HERE / f"thesis-{kind}.svg"


def dst_png(kind: str) -> pathlib.Path:
    """300 dpi PNG output path (previews). Caller: render.*; callee: none."""
    name = "preview-" + kind
    return HERE / f"{name}.png"


def dst_pdf(kind: str) -> pathlib.Path:
    """Vector PDF output path for a panel/jacket. Caller: render.*; callee: none."""
    name = "thesis-" + kind
    if kind == "inside":
        name = "thesis-inside"
    return HERE / f"{name}.pdf"


def run(args) -> subprocess.CompletedProcess:
    """Run rsvg-convert, raising on failure. Caller: render.*; callee: none."""
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"rsvg-convert failed: {' '.join(args)} :: {proc.stderr}")
    return proc


def render_png(kind: str) -> None:
    """Rasterize one SVG to a 300 dpi PNG preview (explicit pixel size). Caller: main; callee: run."""
    out = dst_png(kind)
    w, h = sizepx(kind)
    run(["rsvg-convert", "-w", str(w), "-h", str(h), "-o", str(out), str(src(kind))])
    print(f"wrote {out.name} ({w}x{h})")


def render_pdf(kind: str) -> None:
    """Convert one SVG to a vector PDF (print). Caller: main; callee: run."""
    out = dst_pdf(kind)
    run(["rsvg-convert", "--format=pdf", "-o", str(out), str(src(kind))])
    print(f"wrote {out.name}")


def sizepx(kind: str, dpi: int = DPI) -> tuple[int, int]:
    """PNG pixel size for a kind at the given dpi (pt x dpi/72). Caller: render_png/main; callee: none."""
    from cover_spec import W, H, SB, BLEED
    if kind == "spine":
        w, h = SB, H
    elif kind in (JACKET, INSIDE):
        w, h = BLEED + W + SB + W + BLEED, H + 2 * BLEED
    else:
        w, h = W, H
    return round(w / 72 * dpi), round(h / 72 * dpi)


def main() -> None:
    """Render all PNGs (panels + jacket + inside) and vector PDFs (panels + jacket). Callers: CLI."""
    for kind in PANELS:
        render_png(kind)
        render_pdf(kind)
    for kind in (JACKET, INSIDE):
        render_png(kind)
        if kind == JACKET:
            render_pdf(kind)
    for kind in PANELS + (JACKET, INSIDE):
        print(f"{kind}: rendered {sizepx(kind)} px @300dpi")


if __name__ == "__main__":
    main()