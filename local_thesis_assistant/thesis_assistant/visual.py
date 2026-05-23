from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path


@dataclass
class VisualResult:
    input_docx: str
    pdf_path: str
    page_images: list[str]
    page_count: int
    issues: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @property
    def ok(self) -> bool:
        return not self.issues


def export_docx_to_pdf(docx_path: str | Path, output_dir: str | Path) -> Path:
    if os.environ.get("THESIS_ASSISTANT_ENABLE_WORD_COM_VISUAL") != "1":
        raise RuntimeError(
            "视觉验证需要启动 Microsoft Word COM。为避免隐藏弹窗导致后台卡死，默认不强制启动；"
            "确认本机可交互运行 Word 后，设置 THESIS_ASSISTANT_ENABLE_WORD_COM_VISUAL=1 再重试。"
        )
    source = Path(docx_path).resolve()
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{source.stem}.pdf"
    try:
        import win32com.client  # type: ignore
    except Exception as exc:
        raise RuntimeError("视觉验证需要 Word COM 或其他 DOCX 转 PDF 工具；当前无法导入 win32com.client。") from exc

    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        document = word.Documents.Open(str(source))
        try:
            document.SaveAs(str(target.resolve()), FileFormat=17)
        finally:
            document.Close(False)
    finally:
        word.Quit()
    if not target.exists():
        raise RuntimeError(f"Word COM 未生成 PDF：{target}")
    return target


def _is_blank_image(image) -> bool:
    gray = image.convert("L")
    histogram = gray.histogram()
    total = sum(histogram)
    if total == 0:
        return True
    whiteish = sum(histogram[245:])
    return whiteish / total > 0.995


def render_pdf_pages(pdf_path: str | Path, output_dir: str | Path, scale: float = 1.5) -> tuple[list[Path], list[str]]:
    try:
        import pypdfium2 as pdfium  # type: ignore
    except Exception as exc:
        raise RuntimeError("视觉验证需要 pypdfium2 渲染 PDF 页面；请安装 pypdfium2 后重试。") from exc

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(pdf_path))
    images: list[Path] = []
    warnings: list[str] = []
    try:
        for index in range(len(pdf)):
            page = pdf[index]
            bitmap = page.render(scale=scale)
            pil_image = bitmap.to_pil()
            image_path = out_dir / f"page_{index + 1:03d}.png"
            pil_image.save(image_path)
            images.append(image_path)
            if _is_blank_image(pil_image):
                warnings.append(f"第 {index + 1} 页疑似空白页")
    finally:
        pdf.close()
    return images, warnings


def visual_verify_docx(docx_path: str | Path, output_dir: str | Path) -> VisualResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    issues: list[str] = []
    warnings: list[str] = []
    pdf_path = ""
    images: list[Path] = []
    try:
        pdf = export_docx_to_pdf(docx_path, out_dir)
        pdf_path = str(pdf)
    except Exception as exc:
        issues.append(str(exc))
        result = VisualResult(str(docx_path), pdf_path, [], 0, issues, warnings)
        (out_dir / "visual_report.json").write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return result

    try:
        images, render_warnings = render_pdf_pages(pdf_path, out_dir / "pages")
        warnings.extend(render_warnings)
    except Exception as exc:
        issues.append(str(exc))

    result = VisualResult(
        input_docx=str(docx_path),
        pdf_path=pdf_path,
        page_images=[str(path) for path in images],
        page_count=len(images),
        issues=issues,
        warnings=warnings,
    )
    (out_dir / "visual_report.json").write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return result
