from __future__ import annotations

from docx.oxml.ns import qn
from docx.shared import Pt


def set_run_font(run, east_asia: str, ascii_font: str, size_pt: float, bold: bool | None = None) -> None:
    run.font.name = ascii_font
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:eastAsia"), east_asia)
    run.font.size = Pt(size_pt)
    if bold is not None:
        run.bold = bold


def get_run_east_asia_font(run) -> str | None:
    rpr = run._element.rPr
    if rpr is None or rpr.rFonts is None:
        return None
    return rpr.rFonts.get(qn("w:eastAsia"))
