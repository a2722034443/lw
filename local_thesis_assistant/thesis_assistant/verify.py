from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from .audit import AuditResult, audit_document, write_audit_json, write_audit_markdown
from .visual import VisualResult, visual_verify_docx


@dataclass
class VerificationResult:
    audit: AuditResult
    visual: VisualResult | None

    def to_dict(self) -> dict[str, object]:
        return {
            "audit": self.audit.to_dict(),
            "visual": self.visual.to_dict() if self.visual else None,
            "ok": self.ok,
        }

    @property
    def ok(self) -> bool:
        return not self.audit.has_errors and (self.visual is None or self.visual.ok)


def verify_document(
    input_path: str | Path,
    profile_path: str | Path | None = None,
    output_dir: str | Path = "verify_output",
    visual: bool = False,
) -> VerificationResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    audit = audit_document(input_path, profile_path)
    write_audit_json(audit, out_dir / "audit.json")
    write_audit_markdown(audit, out_dir / "audit.md")
    visual_result = visual_verify_docx(input_path, out_dir / "visual") if visual else None
    result = VerificationResult(audit, visual_result)
    (out_dir / "verify.json").write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return result
