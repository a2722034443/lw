from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

from .ooxml import get_run_east_asia_font
from .rules import ThesisRules, default_rules


ALIGNMENT_NAME = {
    WD_ALIGN_PARAGRAPH.CENTER: "center",
    WD_ALIGN_PARAGRAPH.LEFT: "left",
    WD_ALIGN_PARAGRAPH.RIGHT: "right",
    WD_ALIGN_PARAGRAPH.JUSTIFY: "both",
}


@dataclass
class Finding:
    code: str
    severity: str
    location: str
    message: str
    expected: str
    actual: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _cm(value) -> float:
    return round(value.cm, 2)


def _font_size(run) -> float | None:
    if run.font.size is None:
        return None
    return round(run.font.size.pt, 1)


def _is_heading(text: str) -> int | None:
    if re.match(r"^第[一二三四五六七八九十\d]+章", text):
        return 1
    if re.match(r"^\d+\.\d+\s+", text):
        return 2
    if re.match(r"^\d+\.\d+\.\d+\s+", text):
        return 3
    return None


def _is_caption(text: str) -> bool:
    return bool(re.match(r"^[图表]\d+(\.\d+)?\s+", text.strip()))


def _is_reference_heading(text: str) -> bool:
    return text.strip() in {"参考文献", "References", "REFERENCE"}


def check_document(path: str | Path, rules: ThesisRules | None = None) -> list[Finding]:
    active_rules = rules or default_rules()
    doc = Document(str(path))
    findings: list[Finding] = []

    if doc.sections:
        section = doc.sections[0]
        expected_margins = active_rules.margins
        margin_checks = [
            ("top", _cm(section.top_margin), expected_margins.top_cm, "上边距"),
            ("bottom", _cm(section.bottom_margin), expected_margins.bottom_cm, "下边距"),
            ("left", _cm(section.left_margin), expected_margins.left_cm, "左边距"),
            ("right", _cm(section.right_margin), expected_margins.right_cm, "右边距"),
        ]
        for code, actual, expected, label in margin_checks:
            if abs(actual - expected) > 0.08:
                findings.append(
                    Finding(
                        f"page_margin_{code}",
                        "error",
                        "section[0]",
                        f"{label}不符合规则",
                        f"{expected} cm",
                        f"{actual} cm",
                    )
                )

    citation_numbers: list[int] = []
    figure_numbers: list[str] = []
    table_numbers: list[str] = []
    in_references = False

    for idx, paragraph in enumerate(doc.paragraphs):
        text = paragraph.text.strip()
        if not text:
            continue
        if _is_reference_heading(text):
            in_references = True
        for match in re.finditer(active_rules.reference.citation_pattern, text):
            citation_numbers.append(int(match.group(1)))
        if text.startswith("图"):
            match = re.match(r"^图(\d+(?:\.\d+)?)", text)
            if match:
                figure_numbers.append(match.group(1))
        if text.startswith("表"):
            match = re.match(r"^表(\d+(?:\.\d+)?)", text)
            if match:
                table_numbers.append(match.group(1))

        level = _is_heading(text)
        if level:
            rule = next((item for item in active_rules.headings if item.level == level), None)
            if rule and paragraph.runs:
                run = paragraph.runs[0]
                actual_font = get_run_east_asia_font(run) or run.font.name or ""
                actual_size = _font_size(run)
                actual_alignment = ALIGNMENT_NAME.get(paragraph.alignment, "inherit")
                if rule.font_east_asia not in actual_font:
                    findings.append(
                        Finding("heading_font", "warning", f"paragraph[{idx}]", "标题字体可能不符合规则", rule.font_east_asia, actual_font or "未显式设置")
                    )
                if actual_size is not None and abs(actual_size - rule.font_size_pt) > 0.2:
                    findings.append(
                        Finding("heading_size", "warning", f"paragraph[{idx}]", "标题字号不符合规则", f"{rule.font_size_pt} pt", f"{actual_size} pt")
                    )
                if actual_alignment != "inherit" and actual_alignment != rule.alignment:
                    findings.append(
                        Finding("heading_alignment", "warning", f"paragraph[{idx}]", "标题对齐方式不符合规则", rule.alignment, actual_alignment)
                    )
            continue

        if _is_caption(text):
            expected = active_rules.caption
            if paragraph.runs:
                run = paragraph.runs[0]
                size = _font_size(run)
                actual_alignment = ALIGNMENT_NAME.get(paragraph.alignment, "inherit")
                if size is not None and abs(size - expected.font_size_pt) > 0.2:
                    findings.append(
                        Finding("caption_size", "warning", f"paragraph[{idx}]", "图表题注字号不符合规则", f"{expected.font_size_pt} pt", f"{size} pt")
                    )
                if actual_alignment != "inherit" and actual_alignment != expected.alignment:
                    findings.append(
                        Finding("caption_alignment", "warning", f"paragraph[{idx}]", "图表题注未居中", expected.alignment, actual_alignment)
                    )
            continue

        if in_references:
            continue

        if paragraph.runs:
            run = paragraph.runs[0]
            size = _font_size(run)
            east_font = get_run_east_asia_font(run) or run.font.name or ""
            if size is not None and abs(size - active_rules.body.font_size_pt) > 0.2:
                findings.append(
                    Finding("body_size", "warning", f"paragraph[{idx}]", "正文字号不符合规则", f"{active_rules.body.font_size_pt} pt", f"{size} pt")
                )
            if east_font and active_rules.body.font_east_asia not in east_font:
                findings.append(
                    Finding("body_font", "warning", f"paragraph[{idx}]", "正文字体不符合规则", active_rules.body.font_east_asia, east_font)
                )

    if citation_numbers:
        first_seen: list[int] = []
        for number in citation_numbers:
            if number not in first_seen:
                first_seen.append(number)
        if first_seen != sorted(first_seen) or first_seen != list(range(1, max(first_seen) + 1)):
            findings.append(
                Finding(
                    "citation_order",
                    "error",
                    "body",
                    "正文引用首次出现顺序不连续或未递增",
                    "1..N 顺序递增",
                    ",".join(map(str, first_seen)),
                )
            )

    for label, numbers, code in [("图号", figure_numbers, "figure_number"), ("表号", table_numbers, "table_number")]:
        duplicates = sorted({item for item in numbers if numbers.count(item) > 1})
        if duplicates:
            findings.append(
                Finding(code, "error", "captions", f"{label}存在重复", "不重复", ",".join(duplicates))
            )

    return findings

