from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any


@dataclass
class PageMargins:
    top_cm: float = 2.5
    bottom_cm: float = 2.5
    left_cm: float = 2.8
    right_cm: float = 2.5


@dataclass
class ParagraphRule:
    font_east_asia: str = "宋体"
    font_ascii: str = "Times New Roman"
    font_size_pt: float = 12.0
    line_spacing: float = 1.25
    line_spacing_rule: str = "auto"
    first_line_indent_chars: float = 2.0
    left_indent_chars: float = 0.0
    right_indent_chars: float = 0.0
    special_indent: str = "first_line"
    space_before_lines: float = 0.0
    space_after_lines: float = 0.0
    alignment: str = "both"
    outline_level: int = 9
    text_direction: str = "ltr"
    adjust_right_indent: bool = True
    snap_to_grid: bool = True
    widow_control: bool = True
    keep_with_next: bool = False
    keep_together: bool = False
    page_break_before: bool = False
    kinsoku: bool = True
    word_wrap: bool = False
    overflow_punctuation: bool = True
    top_line_punctuation: bool = False
    auto_space_east_asian_latin: bool = True
    auto_space_east_asian_digit: bool = True
    text_alignment: str = "auto"


@dataclass
class HeadingRule:
    level: int
    font_east_asia: str
    font_ascii: str
    font_size_pt: float
    bold: bool
    alignment: str
    page_break_before: bool = False


@dataclass
class CaptionRule:
    font_east_asia: str = "宋体"
    font_ascii: str = "Times New Roman"
    font_size_pt: float = 10.5
    alignment: str = "center"
    figure_prefix: str = "图"
    table_prefix: str = "表"


@dataclass
class ReferenceRule:
    title: str = "参考文献"
    citation_pattern: str = r"\[(\d+)\]"
    ordered_numeric: bool = True


@dataclass
class ThesisRules:
    name: str = "通用本科毕业设计格式"
    margins: PageMargins = field(default_factory=PageMargins)
    body: ParagraphRule = field(default_factory=ParagraphRule)
    caption: CaptionRule = field(default_factory=CaptionRule)
    reference: ReferenceRule = field(default_factory=ReferenceRule)
    headings: tuple[HeadingRule, ...] = field(
        default_factory=lambda: (
            HeadingRule(1, "黑体", "Times New Roman", 15.0, True, "center", True),
            HeadingRule(2, "黑体", "Times New Roman", 14.0, True, "left", False),
            HeadingRule(3, "宋体", "Times New Roman", 12.0, True, "left", False),
        )
    )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["headings"] = [asdict(h) for h in self.headings]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ThesisRules":
        margins = PageMargins(**data.get("margins", {}))
        body = ParagraphRule(**data.get("body", {}))
        caption = CaptionRule(**data.get("caption", {}))
        reference = ReferenceRule(**data.get("reference", {}))
        heading_data = data.get("headings")
        if heading_data:
            headings = tuple(HeadingRule(**item) for item in heading_data)
        else:
            headings = cls().headings
        return cls(
            name=data.get("name", "通用本科毕业设计格式"),
            margins=margins,
            body=body,
            caption=caption,
            reference=reference,
            headings=headings,
        )


def default_rules() -> ThesisRules:
    return ThesisRules()


def load_rules(path: str | Path | None) -> ThesisRules:
    if path is None:
        return default_rules()
    rule_path = Path(path)
    data = json.loads(rule_path.read_text(encoding="utf-8"))
    return ThesisRules.from_dict(data)


def save_rules(rules: ThesisRules, path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(rules.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
