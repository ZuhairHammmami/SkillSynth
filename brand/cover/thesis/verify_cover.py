#!/usr/bin/env python3
"""Validate the SkillSynth thesis cover: text collisions, safe margins, and the Arabic spine-right layout.

Mirrors the layered-validator pattern of the pptx office validators (one validate_* check per concern,
each returning bool). Text is measured with fontTools against the real installed El Messiri face so
collisions / safe-box violations are detected in print points. Callers: CLI.

Run: python3 verify_cover.py   (expects cover_spec.py / build_covers.py already run)
"""
from __future__ import annotations
import pathlib
import subprocess

from fontTools.ttLib import TTFont

HERE = pathlib.Path(__file__).resolve().parent

SAFE = 27.0          # safe-box inset (pt) from every trim edge
PAD = 6.0            # required clearance between a name and the identity-card inner edge (pt)
AR_FACE = "El Messiri"


class CoverValidator:
    """Layered checks over the thesis cover geometry and the generated jacket SVG."""

    def __init__(self):
        self._ar = self._resolve_ar_font()
        self.errors: list[str] = []

    # -- measurement helpers ------------------------------------------------
    @staticmethod
    def _resolve_ar_font() -> str:
        """Resolve the installed El Messiri TTF path via fontconfig. Caller: __init__; callee: none."""
        out = subprocess.run(["fc-match", "--format=%{file}", AR_FACE],
                             capture_output=True, text=True).stdout.strip()
        return out

    def text_width(self, text: str, size: float) -> float:
        """Advance width of text at size (pt) using the resolved Arabic face. Caller: all checks; callee: none."""
        f = TTFont(self._ar)
        upm = f["head"].unitsPerEm
        cmap, hmtx = f.getBestCmap(), f["hmtx"]
        adv = 0.0
        for ch in text:
            cp = ord(ch)
            if cp in cmap:
                adv += hmtx[cmap[cp]][0]
        return adv / upm * size

    # -- layered checks -----------------------------------------------------
    def validate_safe_box(self) -> bool:
        """Every centred Arabic text element stays fully inside the 27pt safe box (measured width). Caller: validate."""
        from cover_spec import CX, W, R_EDGE, DESC_YS, ABSTRACT, LETTERHEAD_YS
        rows = [(DESC_YS[0], 13.85, "منظومة ذكية للتعلم التكيفي وبناء المهارات", "description1"),
                (DESC_YS[1], 13.85, "تُرسم مسارًا مهنيًا شخصيًا خطوة بخطوة", "description2")]
        rows += [(206 + i * 32, 13.85, line, f"abstract{i}") for i, line in enumerate(ABSTRACT)]
        for y, size, text, tag in rows:
            half = self.text_width(text, size) / 2
            ok = (CX - half >= SAFE) and (CX + half <= W - SAFE) and (y - size >= SAFE)
            if not ok:
                self.errors.append(f"{tag} ' {text} ' spans x={CX - half:.1f}..{CX + half:.1f} (safe {SAFE}..{W - SAFE})")
        for base, text, size, tag in ((LETTERHEAD_YS[0], "جامعة حلب", 19.18, "letterhead1"),
                                      (LETTERHEAD_YS[1], "كلية الهندسة المعلوماتية", 15.77, "letterhead2"),
                                      (LETTERHEAD_YS[2], "مشروع السنة الرابعة", 13.85, "letterhead3")):
            left = R_EDGE - self.text_width(text, size)
            if left < SAFE:
                self.errors.append(f"{tag} left edge {left:.1f} < {SAFE}")
        return not self.errors

    def validate_name_card(self) -> bool:
        """Author and supervisor names clear the identity-card inner edges by at least PAD. Caller: validate."""
        from cover_spec import CX, AUTHORS, SUPS, AUTH_COLS, AUTH_ROWS, SUP_COLS, NAME_SIZE
        card_l, card_r = CX - 172 + 6, CX + 172 - 6
        for i, name in enumerate(AUTHORS, 1):
            x = AUTH_COLS[(i - 1) % 2]
            half = self.text_width(name, NAME_SIZE) / 2
            if not ((x - half >= card_l + PAD) and (x + half <= card_r - PAD)):
                self.errors.append(f"author{i} spans x={x - half:.1f}..{x + half:.1f}"
                                   f" (card inner {card_l}..{card_r}, pad {PAD})")
        for name, x in zip(SUPS, SUP_COLS):
            half = self.text_width(name, NAME_SIZE) / 2
            if not ((x - half >= card_l + PAD) and (x + half <= card_r - PAD)):
                self.errors.append(f"supervisor ' {name} ' spans x={x - half:.1f}..{x + half:.1f}"
                                   f" (card inner {card_l}..{card_r}, pad {PAD})")
        return not self.errors

    def validate_arabic_spine_right(self) -> bool:
        """Jacket lays front | spine | back so the spine bonds to the front cover's RIGHT edge. Caller: validate."""
        import xml.etree.ElementTree as ET
        from cover_spec import BLEED, W, SB
        root = ET.parse(HERE / "thesis-jacket.svg").getroot()
        ns = {"s": "http://www.w3.org/2000/svg"}
        uses = []
        for use in root.findall(".//s:use", ns):
            href = use.get("{http://www.w3.org/1999/xlink}href") or use.get("href") or ""
            tr = use.get("transform") or "translate(0 0)"
            x = float(tr.split("translate(")[1].split(" ")[0])
            uses.append((href, x))
        front_x = min(x for href, x in uses if "front" in href)
        spine_x = min(x for href, x in uses if "spine" in href)
        if spine_x != round(front_x + W, 2):
            self.errors.append(f"spine x={spine_x:.1f} != front x + W = {front_x + W:.1f}"
                               " (front must sit immediately LEFT of spine)")
        return not self.errors

    def validate(self) -> bool:
        """Run every layered check and print PASSED/FAILED per group; return the overall verdict. Callers: CLI."""
        groups = (("safe box", self.validate_safe_box), ("name card", self.validate_name_card),
                  ("spine-right (front|spine|back)", self.validate_arabic_spine_right))
        all_ok = True
        for label, check in groups:
            self.errors.clear()
            ok = check()
            all_ok = all_ok and ok
            print(f"{'PASSED' if ok else 'FAILED'} - {label}")
            for err in self.errors:
                print(f"   {err}")
        print("COVER CHECK:", "ALL PASS" if all_ok else "FAILED")
        return all_ok


def main() -> int:
    """Entry point: validate the cover. Callers: CLI."""
    return 0 if CoverValidator().validate() else 1


if __name__ == "__main__":
    raise SystemExit(main())