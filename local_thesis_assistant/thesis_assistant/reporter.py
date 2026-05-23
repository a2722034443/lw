from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .checker import Finding


def write_json_report(findings: Iterable[Finding], output_path: str | Path) -> Path:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = [finding.to_dict() for finding in findings]
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def write_markdown_report(findings: Iterable[Finding], output_path: str | Path) -> Path:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rows = list(findings)
    lines = [
        "# 论文格式检查报告",
        "",
        f"- 问题总数：{len(rows)}",
        f"- 错误：{sum(1 for item in rows if item.severity == 'error')}",
        f"- 警告：{sum(1 for item in rows if item.severity == 'warning')}",
        "",
        "| 编码 | 级别 | 位置 | 问题 | 期望 | 实际 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            f"| {item.code} | {item.severity} | {item.location} | {item.message} | {item.expected} | {item.actual} |"
        )
    target.write_text("\n".join(lines), encoding="utf-8")
    return target

