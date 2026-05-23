from __future__ import annotations

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

from .rules import ParagraphRule


BOOL_TAGS = {
    "adjust_right_indent": "w:adjustRightInd",
    "snap_to_grid": "w:snapToGrid",
    "widow_control": "w:widowControl",
    "keep_with_next": "w:keepNext",
    "keep_together": "w:keepLines",
    "page_break_before": "w:pageBreakBefore",
    "kinsoku": "w:kinsoku",
    "word_wrap": "w:wordWrap",
    "overflow_punctuation": "w:overflowPunct",
    "top_line_punctuation": "w:topLinePunct",
    "auto_space_east_asian_latin": "w:autoSpaceDE",
    "auto_space_east_asian_digit": "w:autoSpaceDN",
}


def _ppr(paragraph):
    return paragraph._p.get_or_add_pPr()


def _child(parent, tag: str):
    node = parent.find(qn(tag))
    if node is None:
        node = OxmlElement(tag)
        parent.append(node)
    return node


def _remove(parent, tag: str) -> None:
    node = parent.find(qn(tag))
    if node is not None:
        parent.remove(node)


def _set_bool(parent, tag: str, enabled: bool) -> None:
    node = _child(parent, tag)
    node.set(qn("w:val"), "1" if enabled else "0")


def _get_bool(parent, tag: str) -> bool | None:
    node = parent.find(qn(tag))
    if node is None:
        return None
    value = node.get(qn("w:val"))
    return value not in {"0", "false", "False"}


def _chars_to_twips(chars: float) -> int:
    return int(round(chars * 240))


def apply_paragraph_rule(paragraph, rule: ParagraphRule) -> None:
    fmt = paragraph.paragraph_format
    fmt.space_before = Pt(0)
    fmt.space_after = Pt(0)
    fmt.keep_with_next = rule.keep_with_next
    fmt.keep_together = rule.keep_together
    fmt.page_break_before = rule.page_break_before
    fmt.widow_control = rule.widow_control

    if rule.special_indent == "none":
        fmt.first_line_indent = None
    elif rule.special_indent == "hanging":
        fmt.first_line_indent = Pt(-12 * rule.first_line_indent_chars)
    else:
        fmt.first_line_indent = Pt(12 * rule.first_line_indent_chars)

    ppr = _ppr(paragraph)
    ind = _child(ppr, "w:ind")
    ind.set(qn("w:leftChars"), str(int(round(rule.left_indent_chars * 100))))
    ind.set(qn("w:rightChars"), str(int(round(rule.right_indent_chars * 100))))
    ind.set(qn("w:left"), str(_chars_to_twips(rule.left_indent_chars)))
    ind.set(qn("w:right"), str(_chars_to_twips(rule.right_indent_chars)))
    if rule.special_indent == "none":
        for attr in ["w:firstLine", "w:firstLineChars", "w:hanging", "w:hangingChars"]:
            ind.attrib.pop(qn(attr), None)
    elif rule.special_indent == "hanging":
        ind.attrib.pop(qn("w:firstLine"), None)
        ind.attrib.pop(qn("w:firstLineChars"), None)
        ind.set(qn("w:hangingChars"), str(int(round(rule.first_line_indent_chars * 100))))
        ind.set(qn("w:hanging"), str(_chars_to_twips(rule.first_line_indent_chars)))
    else:
        ind.attrib.pop(qn("w:hanging"), None)
        ind.attrib.pop(qn("w:hangingChars"), None)
        ind.set(qn("w:firstLineChars"), str(int(round(rule.first_line_indent_chars * 100))))
        ind.set(qn("w:firstLine"), str(_chars_to_twips(rule.first_line_indent_chars)))

    spacing = _child(ppr, "w:spacing")
    spacing.set(qn("w:beforeLines"), str(int(round(rule.space_before_lines * 100))))
    spacing.set(qn("w:afterLines"), str(int(round(rule.space_after_lines * 100))))
    if rule.line_spacing_rule == "exact":
        spacing.set(qn("w:lineRule"), "exact")
        spacing.set(qn("w:line"), str(int(round(rule.line_spacing * 20))))
    elif rule.line_spacing_rule == "at_least":
        spacing.set(qn("w:lineRule"), "atLeast")
        spacing.set(qn("w:line"), str(int(round(rule.line_spacing * 20))))
    else:
        spacing.set(qn("w:lineRule"), "auto")
        spacing.set(qn("w:line"), str(int(round(rule.line_spacing * 240))))
        fmt.line_spacing = rule.line_spacing

    if rule.outline_level >= 0:
        outline = _child(ppr, "w:outlineLvl")
        outline.set(qn("w:val"), str(rule.outline_level))
    if rule.text_direction == "rtl":
        _set_bool(ppr, "w:bidi", True)
    else:
        _remove(ppr, "w:bidi")
    text_alignment = _child(ppr, "w:textAlignment")
    text_alignment.set(qn("w:val"), rule.text_alignment)

    for field, tag in BOOL_TAGS.items():
        _set_bool(ppr, tag, bool(getattr(rule, field)))


def paragraph_ooxml_summary(paragraph) -> dict[str, object]:
    ppr = paragraph._p.pPr
    if ppr is None:
        return {}
    spacing = ppr.find(qn("w:spacing"))
    ind = ppr.find(qn("w:ind"))
    outline = ppr.find(qn("w:outlineLvl"))
    text_alignment = ppr.find(qn("w:textAlignment"))
    data: dict[str, object] = {}
    if ind is not None:
        data["left_chars"] = ind.get(qn("w:leftChars"))
        data["right_chars"] = ind.get(qn("w:rightChars"))
        data["first_line_chars"] = ind.get(qn("w:firstLineChars"))
        data["hanging_chars"] = ind.get(qn("w:hangingChars"))
    if spacing is not None:
        data["before_lines"] = spacing.get(qn("w:beforeLines"))
        data["after_lines"] = spacing.get(qn("w:afterLines"))
        data["line"] = spacing.get(qn("w:line"))
        data["line_rule"] = spacing.get(qn("w:lineRule"))
    if outline is not None:
        data["outline_level"] = outline.get(qn("w:val"))
    if text_alignment is not None:
        data["text_alignment"] = text_alignment.get(qn("w:val"))
    for field, tag in BOOL_TAGS.items():
        data[field] = _get_bool(ppr, tag)
    data["text_direction"] = "rtl" if _get_bool(ppr, "w:bidi") else "ltr"
    return data
