import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


REF_RE = re.compile(r"^\s*\[([0-9]+)\]\s*(.+?)\s*$")
JOURNAL_RE = re.compile(r"\[J\]\.?", re.IGNORECASE)
YEAR_VOL_ISSUE_PAGES_RE = re.compile(r"(19|20)\d{2}\s*[,，]\s*[^,，:：]+?\([^)）]+[)）]\s*[:：]\s*\d+[-－—]\d+")
YEAR_ONLY_RE = re.compile(r"(19|20)\d{2}\s*\.?$")


def load_references(path: Path) -> list[tuple[int, str]]:
    refs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = REF_RE.match(line.strip())
        if m:
            refs.append((int(m.group(1)), m.group(2).strip()))
    return refs


def validate_reference(num: int, text: str) -> list[str]:
    issues: list[str] = []
    if "．" not in text and "." not in text:
        issues.append("缺少责任者与题名之间的点号")
    first_dot = min([i for i in [text.find("．"), text.find(".")] if i >= 0], default=-1)
    if first_dot <= 0:
        issues.append("缺少责任者项，或责任者与题名间没有点号分隔")
    if JOURNAL_RE.search(text):
        if not YEAR_VOL_ISSUE_PAGES_RE.search(text):
            if YEAR_ONLY_RE.search(text):
                issues.append("期刊文献只有年份，缺少卷号、期号和页码")
            elif re.search(r"(19|20)\d{2}\s*[,，]\s*[^:：]+?\([^)）]+[)）]\s*\.?$", text):
                issues.append("期刊文献缺少页码")
            else:
                issues.append("期刊文献应包含年、卷(期)：页码")
    if "[J]" not in text and "[D]" not in text and "[M]" not in text and "[C]" not in text and "[EB/OL]" not in text:
        issues.append("缺少文献类型标识")
    return [f"[{num}] {issue}" for issue in issues]


def validate_body_citations(body_path: Path, ref_nums: list[int]) -> list[str]:
    text = body_path.read_text(encoding="utf-8")
    citations = [int(x) for x in re.findall(r"\[([0-9]+)\]", text)]
    issues: list[str] = []
    seen = []
    for n in citations:
        if n not in seen:
            seen.append(n)
    if seen and seen != sorted(seen):
        issues.append("正文首次引用顺序不是递增顺序")
    missing_refs = [n for n in seen if n not in ref_nums]
    if missing_refs:
        issues.append("正文引用在参考文献表中不存在：" + ",".join(map(str, missing_refs)))
    unused = [n for n in ref_nums if n not in seen]
    if unused:
        issues.append("参考文献未在正文中引用：" + ",".join(map(str, unused)))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 GB/T 7714 顺序编码参考文献的常见格式问题。")
    parser.add_argument("references", type=Path, help="包含 [1] ... 参考文献行的 UTF-8 文本文件")
    parser.add_argument("--body", type=Path, help="可选：包含正文引用的 UTF-8 文本文件")
    args = parser.parse_args()

    refs = load_references(args.references)
    if not refs:
        print("未找到形如 [1] 的参考文献条目")
        return 1
    issues: list[str] = []
    nums = [num for num, _ in refs]
    if nums != list(range(nums[0], nums[0] + len(nums))):
        issues.append("参考文献编号不连续")
    for num, text in refs:
        issues.extend(validate_reference(num, text))
    if args.body:
        issues.extend(validate_body_citations(args.body, nums))
    if issues:
        print("\n".join(issues))
        return 1
    print(f"通过基础检查：{len(refs)} 条参考文献")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
