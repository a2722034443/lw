from __future__ import annotations

from pathlib import Path
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

from .ooxml import set_run_font
from .paragraph_ooxml import apply_paragraph_rule
from .rules import ThesisRules, default_rules


ALIGNMENT_MAP = {
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
    "both": WD_ALIGN_PARAGRAPH.JUSTIFY,
}


def _heading_level(text: str) -> int | None:
    if re.match(r"^第[一二三四五六七八九十\d]+章", text):
        return 1
    if re.match(r"^\d+\.\d+\.\d+\s+", text):
        return 3
    if re.match(r"^\d+\.\d+\s+", text):
        return 2
    return None


def _is_caption(text: str) -> bool:
    return bool(re.match(r"^[图表]\d+(\.\d+)?\s+", text.strip()))


def _apply_paragraph_spacing(paragraph, line_spacing: float, first_line_chars: float = 0) -> None:
    paragraph.paragraph_format.line_spacing = line_spacing
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)
    if first_line_chars:
        paragraph.paragraph_format.first_line_indent = Pt(12 * first_line_chars)


def normalize_docx(input_path: str | Path, output_path: str | Path, rules: ThesisRules | None = None) -> Path:
    active_rules = rules or default_rules()
    document = Document(str(input_path))

    for section in document.sections:
        section.top_margin = Cm(active_rules.margins.top_cm)
        section.bottom_margin = Cm(active_rules.margins.bottom_cm)
        section.left_margin = Cm(active_rules.margins.left_cm)
        section.right_margin = Cm(active_rules.margins.right_cm)

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue

        level = _heading_level(text)
        if level:
            rule = next((item for item in active_rules.headings if item.level == level), None)
            if rule:
                paragraph.alignment = ALIGNMENT_MAP[rule.alignment]
                paragraph.paragraph_format.page_break_before = rule.page_break_before
                paragraph.paragraph_format.first_line_indent = Pt(0)
                paragraph.paragraph_format.line_spacing = 1.0
                for run in paragraph.runs:
                    set_run_font(run, rule.font_east_asia, rule.font_ascii, rule.font_size_pt, rule.bold)
            continue

        if _is_caption(text):
            paragraph.alignment = ALIGNMENT_MAP[active_rules.caption.alignment]
            _apply_paragraph_spacing(paragraph, 1.0, 0)
            for run in paragraph.runs:
                set_run_font(
                    run,
                    active_rules.caption.font_east_asia,
                    active_rules.caption.font_ascii,
                    active_rules.caption.font_size_pt,
                    False,
                )
            continue

        paragraph.alignment = ALIGNMENT_MAP[active_rules.body.alignment]
        apply_paragraph_rule(paragraph, active_rules.body)
        for run in paragraph.runs:
            set_run_font(
                run,
                active_rules.body.font_east_asia,
                active_rules.body.font_ascii,
                active_rules.body.font_size_pt,
                False,
            )

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(target))
    return target
