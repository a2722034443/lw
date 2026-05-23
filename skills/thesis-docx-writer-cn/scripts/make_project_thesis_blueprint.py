import argparse
from pathlib import Path


DEFAULT_CHAPTERS = [
    ("摘要与关键词", 800, 0, 0, "研究目的、方法、结果、结论。"),
    ("第1章 绪论", 3000, 2, 0, "背景、意义、研究现状、问题分析、技术路线。"),
    ("第2章 相关技术与理论基础", 3000, 6, 1, "算法、框架、数据库、评价指标、技术对比。"),
    ("第3章 需求分析与可行性分析", 3000, 8, 2, "角色、用例、业务流程、功能和非功能需求、可行性。"),
    ("第4章 系统总体设计", 3200, 10, 1, "架构、模块、数据库、接口、安全、部署。"),
    ("第5章 系统详细设计与实现", 4300, 12, 1, "关键模块、页面或接口、核心代码逻辑、异常处理。"),
    ("第6章 实验、测试与结果分析", 3400, 8, 2, "实验设置、功能测试、性能测试、对比分析、结果讨论。"),
    ("第7章 工程管理、经济决策与社会责任", 1500, 2, 1, "进度、成本、方案决策、法律伦理、隐私安全、环境约束。"),
    ("第8章 总结与展望", 1200, 0, 0, "完成工作、不足、改进方向。"),
]


FIGURE_TYPES = {
    "第1章 绪论": ["研究技术路线图", "论文整体研究流程图"],
    "第2章 相关技术与理论基础": ["算法流程图", "模型训练流程图", "评价指标解释图", "数据处理流程图", "技术栈关系图", "方案对比结构图"],
    "第3章 需求分析与可行性分析": ["系统用例图", "用户活动图", "业务流程图", "数据流图", "功能模块图", "权限关系图", "可行性分析图", "风险约束图"],
    "第4章 系统总体设计": ["系统架构图", "模块结构图", "ER图", "数据库关系图", "接口调用流程图", "安全设计图", "部署结构图", "日志流程图", "异常处理流程图", "数据字典关系图"],
    "第5章 系统详细设计与实现": ["登录页面图", "数据管理页面图", "训练配置页面图", "模型管理页面图", "预测页面图", "结果展示页面图", "报表导出页面图", "核心模块流程图", "接口返回示意图", "权限校验流程图", "文件上传流程图", "系统运行截图"],
    "第6章 实验、测试与结果分析": ["测试流程图", "混淆矩阵图", "ROC曲线图", "指标对比图", "性能测试图", "测试用例执行截图", "错误处理测试图", "消融或方案对比图"],
    "第7章 工程管理、经济决策与社会责任": ["项目进度图", "成本构成图"],
}


TABLE_TYPES = [
    "文献与技术方案对比表",
    "功能需求表",
    "非功能需求表",
    "数据库表结构表",
    "测试用例表",
    "实验指标结果表",
    "工程成本估算表",
    "项目进度计划表",
]


def scale_counts(min_words: int, min_figures: int, min_tables: int):
    base_words = sum(ch[1] for ch in DEFAULT_CHAPTERS)
    word_ratio = max(1.0, min_words / base_words)
    chapters = []
    figure_total = sum(ch[2] for ch in DEFAULT_CHAPTERS)
    table_total = sum(ch[3] for ch in DEFAULT_CHAPTERS)
    figure_gap = max(0, min_figures - figure_total)
    table_gap = max(0, min_tables - table_total)
    for idx, (name, words, figs, tabs, note) in enumerate(DEFAULT_CHAPTERS):
        extra_fig = 1 if figure_gap > 0 and "第" in name and idx % 2 == 0 else 0
        extra_tab = 1 if table_gap > 0 and "第" in name and idx % 3 == 0 else 0
        if extra_fig:
            figure_gap -= 1
        if extra_tab:
            table_gap -= 1
        chapters.append((name, int(round(words * word_ratio)), figs + extra_fig, tabs + extra_tab, note))
    i = 0
    while figure_gap > 0:
        name, words, figs, tabs, note = chapters[2 + (i % 5)]
        chapters[2 + (i % 5)] = (name, words, figs + 1, tabs, note)
        figure_gap -= 1
        i += 1
    i = 0
    while table_gap > 0:
        name, words, figs, tabs, note = chapters[2 + (i % 5)]
        chapters[2 + (i % 5)] = (name, words, figs, tabs + 1, note)
        table_gap -= 1
        i += 1
    return chapters


def build_markdown(title: str, min_words: int, min_figures: int, min_tables: int) -> str:
    chapters = scale_counts(min_words, min_figures, min_tables)
    lines = [
        f"# 《{title}》项目型论文规划",
        "",
        "## 硬性目标",
        "",
        f"- 正文净字数：不少于 {min_words} 字。",
        f"- 图片：不少于 {min_figures} 张，所有图片必须有图号、图题和正文引用。",
        f"- 表格：不少于 {min_tables} 个，默认采用三线表。",
        "- 参考文献：按用户或学校要求，所有条目必须联网核验并在正文引用。",
        "- 交叉引用：优先使用 Word 题注和交叉引用域；若使用静态编号，交付前必须脚本校验。",
        "",
        "## 章节规模分配",
        "",
        "| 章节 | 建议字数 | 图片数 | 表格数 | 写作重点 |",
        "|---|---:|---:|---:|---|",
    ]
    for name, words, figs, tabs, note in chapters:
        lines.append(f"| {name} | {words} | {figs} | {tabs} | {note} |")
    lines.extend(["", "## 图片清单建议", ""])
    fig_no = 1
    for name, _, figs, _, _ in chapters:
        if figs <= 0:
            continue
        types = FIGURE_TYPES.get(name, ["结构图", "流程图", "结果图"])
        lines.append(f"### {name}")
        for i in range(figs):
            lines.append(f"- 图{fig_no}：{types[i % len(types)]}")
            fig_no += 1
        lines.append("")
    lines.extend(["## 表格清单建议", ""])
    tab_no = 1
    for name, _, _, tabs, _ in chapters:
        for i in range(tabs):
            lines.append(f"- 表{tab_no}：{TABLE_TYPES[(tab_no - 1) % len(TABLE_TYPES)]}（建议放在{name}）")
            tab_no += 1
    lines.extend(
        [
            "",
            "## 写作顺序",
            "",
            "1. 先联网确认学校模板、GB/T 7713.1、GB/T 7714 和同类项目论文要求。",
            "2. 先完成文献、数据集、实验、系统截图和图件素材，再写正文。",
            "3. 每章写完后立即补正文引用、图表引用和参考文献编号。",
            "4. 生成 DOCX 后运行 `validate_thesis_docx.py` 检查规模、图表、引用和基础版式。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="生成项目型中文论文的字数、图表和章节规划。")
    parser.add_argument("title", help="论文题目")
    parser.add_argument("-o", "--output", type=Path, help="输出 Markdown 文件路径")
    parser.add_argument("--min-words", type=int, default=20000, help="最低正文净字数")
    parser.add_argument("--min-figures", type=int, default=40, help="最低图片数量")
    parser.add_argument("--min-tables", type=int, default=6, help="最低表格数量")
    args = parser.parse_args()

    text = build_markdown(args.title, args.min_words, args.min_figures, args.min_tables)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
