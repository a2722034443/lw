from __future__ import annotations

import argparse
from pathlib import Path

from .audit import audit_document, write_audit_json, write_audit_markdown
from .checker import check_document
from .doc_reader import can_convert_doc, load_document_info
from .fixer import conservative_fix_docx
from .formatter import normalize_docx
from .profile import inspect_template, write_profile, write_profile_rules
from .reference_links import link_reference_citations, write_reference_link_report
from .reporter import write_json_report, write_markdown_report
from .rules import load_rules
from .verify import verify_document


def main() -> int:
    parser = argparse.ArgumentParser(description="本地论文格式检查与修正助手")
    sub = parser.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect", help="读取文档结构")
    inspect.add_argument("input")

    check = sub.add_parser("check", help="检查 DOCX 格式")
    check.add_argument("input")
    check.add_argument("--rules")
    check.add_argument("--json")
    check.add_argument("--md")

    fmt = sub.add_parser("format", help="按规则修正 DOCX")
    fmt.add_argument("input")
    fmt.add_argument("output")
    fmt.add_argument("--rules")

    diag = sub.add_parser("diag", help="输出环境诊断")

    template = sub.add_parser("template-inspect", help="抽取学校模板画像")
    template.add_argument("template")
    template.add_argument("--out", required=True, help="模板画像 JSON 输出路径")
    template.add_argument("--rules-out", help="可选：同步输出规则 JSON")
    template.add_argument("--work-dir", help="DOC 转 DOCX 的中间目录")

    audit = sub.add_parser("audit", help="全量审查 DOCX 内容、结构和格式")
    audit.add_argument("input")
    audit.add_argument("--profile", help="template-inspect 生成的模板画像 JSON")
    audit.add_argument("--json", help="JSON 报告输出路径")
    audit.add_argument("--md", help="Markdown 报告输出路径")

    fix = sub.add_parser("fix", help="按模板画像保守修正 DOCX")
    fix.add_argument("input")
    fix.add_argument("output")
    fix.add_argument("--profile", help="template-inspect 生成的模板画像 JSON")

    ref_links = sub.add_parser("link-references", help="把正文 [n] 引用链接到文末参考文献书签")
    ref_links.add_argument("input")
    ref_links.add_argument("output")
    ref_links.add_argument("--json", help="链接结果 JSON 报告输出路径")

    verify = sub.add_parser("verify", help="二次审查并可选执行视觉验证")
    verify.add_argument("input")
    verify.add_argument("--profile", help="template-inspect 生成的模板画像 JSON")
    verify.add_argument("--visual", action="store_true", help="使用 Word COM + pypdfium2 执行视觉验证")
    verify.add_argument("--out-dir", required=True, help="验证报告输出目录")

    pipeline = sub.add_parser("pipeline", help="模板抽取、审查、保守修正和验证的一体化流程")
    pipeline.add_argument("input")
    pipeline.add_argument("output")
    pipeline.add_argument("--template", required=True, help="学校模板 .doc/.docx")
    pipeline.add_argument("--visual", action="store_true", help="执行视觉验证")
    pipeline.add_argument("--out-dir", default="local_thesis_assistant/outputs/pipeline", help="流程输出目录")

    args = parser.parse_args()

    if args.command == "diag":
        print(can_convert_doc())
        return 0
    if args.command == "inspect":
        info = load_document_info(args.input)
        print(f"path={info.path}")
        print(f"paragraphs={len(info.paragraphs)}")
        print(f"tables={len(info.tables)}")
        print(f"pictures={info.picture_count}")
        print(f"sections={info.section_count}")
        return 0
    if args.command == "check":
        findings = check_document(args.input, load_rules(args.rules))
        for finding in findings:
            print(f"{finding.severity.upper()} {finding.code} {finding.location}: {finding.message}")
        if args.json:
            write_json_report(findings, args.json)
        if args.md:
            write_markdown_report(findings, args.md)
        return 1 if any(item.severity == "error" for item in findings) else 0
    if args.command == "format":
        normalize_docx(args.input, args.output, load_rules(args.rules))
        print(Path(args.output))
        return 0
    if args.command == "template-inspect":
        profile = inspect_template(args.template, args.work_dir)
        profile_path = write_profile(profile, args.out)
        print(profile_path)
        if args.rules_out:
            print(write_profile_rules(profile, args.rules_out))
        return 0
    if args.command == "audit":
        result = audit_document(args.input, args.profile)
        for finding in result.findings:
            print(f"{finding.severity.upper()} {finding.code} {finding.location}: {finding.message}")
        if args.json:
            write_audit_json(result, args.json)
        if args.md:
            write_audit_markdown(result, args.md)
        print(f"metrics={result.metrics}")
        return 1 if result.has_errors else 0
    if args.command == "fix":
        target = conservative_fix_docx(args.input, args.output, args.profile)
        print(target)
        return 0
    if args.command == "link-references":
        result = link_reference_citations(args.input, args.output)
        print(args.output)
        print(f"linked_citations={result.linked_citations}")
        if result.skipped_citations:
            print("skipped_citations=" + ",".join(result.skipped_citations))
        if args.json:
            write_reference_link_report(result, args.json)
        return 0 if not result.skipped_citations else 1
    if args.command == "verify":
        result = verify_document(args.input, args.profile, args.out_dir, args.visual)
        print(Path(args.out_dir) / "verify.json")
        return 0 if result.ok else 1
    if args.command == "pipeline":
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        profile = inspect_template(args.template, out_dir / "template_work")
        profile_path = write_profile(profile, out_dir / "template_profile.json")
        write_profile_rules(profile, out_dir / "template_rules.json")
        before = audit_document(args.input, profile_path)
        write_audit_json(before, out_dir / "before_audit.json")
        write_audit_markdown(before, out_dir / "before_audit.md")
        fixed = conservative_fix_docx(args.input, args.output, profile_path)
        result = verify_document(fixed, profile_path, out_dir / "verify", args.visual)
        print(f"profile={profile_path}")
        print(f"fixed={fixed}")
        print(f"verify={out_dir / 'verify' / 'verify.json'}")
        return 0 if result.ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
