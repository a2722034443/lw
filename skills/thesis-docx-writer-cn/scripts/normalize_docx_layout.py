import argparse
import shutil
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


FIG_TABLE_PREFIXES = ("图", "表")


def set_run_font(run, east_asia: str, ascii_font: str, size_pt: float | None = None, bold: bool | None = None):
    run.font.name = ascii_font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), east_asia)
    if size_pt is not None:
        run.font.size = Pt(size_pt)
    if bold is not None:
        run.bold = bold


def set_style_font(style, east_asia: str, ascii_font: str, size_pt: float, bold: bool | None = None):
    style.font.name = ascii_font
    style._element.rPr.rFonts.set(qn("w:eastAsia"), east_asia)
    style.font.size = Pt(size_pt)
    if bold is not None:
        style.font.bold = bold


def configure_styles(doc: Document):
    set_style_font(doc.styles["Normal"], "宋体", "Times New Roman", 10.5)
    for name, size in [("Heading 1", 15), ("Heading 2", 14), ("Heading 3", 10.5)]:
        if name in doc.styles:
            set_style_font(doc.styles[name], "黑体", "Times New Roman", size, True)
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.8)
        section.right_margin = Cm(2.5)


def normalize_paragraphs(doc: Document):
    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
        is_heading = p.style and p.style.name.lower().startswith("heading")
        is_caption = text.startswith(FIG_TABLE_PREFIXES)
        if is_heading:
            p.paragraph_format.first_line_indent = None
            p.paragraph_format.line_spacing = 1.5
        elif is_caption:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = None
            p.paragraph_format.line_spacing = 1.0
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.first_line_indent = Cm(0.74)
            p.paragraph_format.line_spacing = 1.5
        for run in p.runs:
            if is_heading:
                set_run_font(run, "黑体", "Times New Roman", None, True)
            elif is_caption:
                set_run_font(run, "宋体", "Times New Roman", 9)
            else:
                set_run_font(run, "宋体", "Times New Roman", 10.5)


def set_update_fields_on_open(path: Path):
    with zipfile.ZipFile(path, "a") as zf:
        settings_name = "word/settings.xml"
        if settings_name not in zf.namelist():
            return
        xml = zf.read(settings_name).decode("utf-8", errors="ignore")
        if "w:updateFields" in xml:
            xml = xml.replace('w:updateFields w:val="false"', 'w:updateFields w:val="true"')
            xml = xml.replace('w:updateFields w:val="0"', 'w:updateFields w:val="true"')
        else:
            marker = "</w:settings>"
            xml = xml.replace(marker, '<w:updateFields w:val="true"/>' + marker)
        zf.writestr(settings_name, xml)


def main() -> int:
    parser = argparse.ArgumentParser(description="按通用中文论文基线规范化 docx 版式，并设置打开时更新域。")
    parser.add_argument("input", type=Path, help="输入 docx")
    parser.add_argument("output", type=Path, help="输出 docx")
    args = parser.parse_args()

    if args.input.resolve() != args.output.resolve():
        shutil.copy2(args.input, args.output)
    doc = Document(args.output)
    configure_styles(doc)
    normalize_paragraphs(doc)
    doc.save(args.output)
    set_update_fields_on_open(args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
