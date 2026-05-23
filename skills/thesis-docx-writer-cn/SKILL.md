---
name: thesis-docx-writer-cn
description: 中文论文与DOCX全流程处理技能。用于用户给出论文题目、研究方向、数据集、学校模板或.docx文件后，需要联网调研论文格式、检索真实文献和数据集、设计并运行实验、撰写论文正文、生成或修改docx、处理参考文献、插入图表、校验格式、提取文本、解包OOXML、转换PDF或图片等任务。
---

# 中文 DOCX 论文全流程

## 核心原则

1. 必须先联网调研，再写论文格式、文献、数据集、实验和图件。用户明确禁止联网时，要说明无法完成真实性核验。
2. 不得编造参考文献、数据集、实验结果、指标、页码、DOI、卷期号或软件版本。
3. 用户提供学校模板时，模板优先于国家标准和通用写法。先读取模板样式，再决定排版。
4. 学术、商业、政府、法律或他人文档默认先备份；需要明显改写时优先使用修订或可回滚副本。
5. 默认中文输出。工具名、命令、库名、标准号、代码参数可以保留英文。
6. 图件默认调用 `diagram-norm-cn`：先查对应图类标准，再生成黑白中文 draw.io XML 或嵌入图件。
7. 写作必须具体、克制、可验证。所有结论来自文献、系统实现、实验记录或测试结果。

## 先读哪个参考文件

- 处理 `.docx` 读取、编辑、解包、打包、修订、注释、转换时，读 `references/docx-workflows.md`。
- 写论文结构、引用、参考文献、图表、格式时，读 `references/thesis-writing-standards.md`。
- 用户要求完整项目论文、2万字、40张图、6个表、严格排版、题注或交叉引用时，读 `references/project-thesis-layout-and-scale.md`。
- 需要找数据集、做实验、记录指标、写实验章节时，读 `references/research-experiment-workflow.md`。
- 用户强调“不要 AI 味”、写摘要、绪论、结论、系统章节时，读 `references/anti-ai-writing.md`。

## 工作流决策

### 用户只给题目

1. 联网检索学校或目标格式要求；没有学校时检索 GB/T 7713.1、GB/T 7714 和相近论文规范。
2. 联网检索近年文献，记录题名、作者、年份、期刊、卷期、页码、DOI 或数据库页。
3. 联网检索可用数据集，记录来源、许可、字段、样本量、下载方式和适用性。
4. 设计实验方案，明确模型、指标、数据划分、随机种子和失败条件。
5. 能运行实验时才写结果；不能运行时只写计划或说明限制。
6. 按模板或规范生成论文结构，再写正文。
7. 若用户要求完整项目论文，先用 `scripts/make_project_thesis_blueprint.py` 生成章节、字数、图表与引用规划；不得直接短文档冒充完整论文。

### 用户给 `.docx` 模板或论文文件

1. 先备份原文件。
2. 用 `scripts/extract_docx_text.py` 提取文本，必要时用 `scripts/inspect_docx_styles.py` 检查样式。
3. 若需要精确修改样式、目录、页眉页脚、批注或修订，先解包 OOXML，再修改副本。
4. 修改后重新提取文本并检查关键段落、图表、引用和参考文献是否存在。

### 用户要求新建 docx

1. 优先检查 Node `docx` 库；若缺失，使用 `python-docx` 生成基础文档。
2. 先定义标题层级、正文样式、图表题注、参考文献样式。
3. 不用手工空格模拟缩进；用段落格式、样式和表格宽度控制版式。
4. 完整项目论文默认目标：正文净字数不少于用户要求，未说明时按不少于20000字规划；图片不少于用户要求，未说明时按不少于40张规划；表格不少于用户要求，未说明时按不少于6个规划。
5. 图题、表题和正文交叉引用优先使用 Word 题注与域；若只能生成静态编号，必须用脚本检查连续性并说明限制。

### 用户要求改参考文献

1. 联网核验每条文献。
2. 使用 GB/T 7714 顺序编码制。
3. 期刊析出文献必须尽量补全作者、题名、期刊名、年、卷、期、页码、DOI。
4. 正文引用顺序必须和文末编号一致。
5. 用 `scripts/validate_gbt_references.py` 做基础格式检查。

## 本地工具状态

本技能创建时，本机已发现：

- 已有：`python-docx`、`lxml`、`defusedxml`。
- 未发现：`pandoc`、`soffice`、`pdftoppm`、Node `docx`。

执行任务时仍要重新运行 `scripts/check_docx_deps.py`，因为环境可能变化。缺失依赖时，不要假装完成转换；使用降级方案或请求用户授权安装。

## 常用脚本

```powershell
python -m local_thesis_assistant.thesis_assistant template-inspect "local_thesis_assistant\大连民族大学本科毕业设计说明书（论文）格式要求-2024.doc.doc" --out local_thesis_assistant\outputs\template_profile.json --rules-out local_thesis_assistant\outputs\template_rules.json
python -m local_thesis_assistant.thesis_assistant audit input.docx --profile local_thesis_assistant\outputs\template_profile.json --json audit.json --md audit.md
python -m local_thesis_assistant.thesis_assistant fix input.docx fixed.docx --profile local_thesis_assistant\outputs\template_profile.json
python -m local_thesis_assistant.thesis_assistant link-references fixed.docx linked.docx --json reference_links.json
python -m local_thesis_assistant.thesis_assistant verify fixed.docx --profile local_thesis_assistant\outputs\template_profile.json --out-dir verify_out --visual
python -m local_thesis_assistant.thesis_assistant pipeline input.docx fixed.docx --template "local_thesis_assistant\大连民族大学本科毕业设计说明书（论文）格式要求-2024.doc.doc" --visual --out-dir local_thesis_assistant\outputs\pipeline
python skills\thesis-docx-writer-cn\scripts\check_docx_deps.py
python skills\thesis-docx-writer-cn\scripts\extract_docx_text.py input.docx -o output.md
python skills\thesis-docx-writer-cn\scripts\inspect_docx_styles.py template.docx
python skills\thesis-docx-writer-cn\scripts\unpack_docx.py input.docx unpacked
python skills\thesis-docx-writer-cn\scripts\pack_docx.py unpacked output.docx
python skills\thesis-docx-writer-cn\scripts\validate_gbt_references.py references.txt --body thesis.txt
python skills\thesis-docx-writer-cn\scripts\make_project_thesis_blueprint.py "论文题目" -o blueprint.md
python skills\thesis-docx-writer-cn\scripts\normalize_docx_layout.py input.docx output.docx
python skills\thesis-docx-writer-cn\scripts\validate_thesis_docx.py thesis.docx --min-chars 20000 --min-figures 40 --min-tables 6
```

## 本地助手一期标准流程

1. 先运行 `template-inspect`。若学校模板是旧版 `.doc` 且本机转换失败，命令会生成通用规则降级画像，并在 `notes` 中写明转换诊断；用户应优先用 Word 手动另存为 `.docx` 后重新抽取。
2. 再运行 `audit`，报告必须覆盖结构、字体字号、段落格式、图表题注、三线表、公式、引用和域代码。
3. 只用 `fix` 做保守修正：样式、WPS/Word 段落属性、页边距、题注样式、表格三线表和打开时更新域；不得自动改写事实、实验结论或未核验参考文献。段落属性覆盖对齐、大纲级别、文字方向、左右缩进、首行/悬挂缩进、段前段后、多倍/固定行距、孤行控制、与下段同页、段中不分页、段前分页、中文首尾字符控制、标点溢出、中文与西文/数字自动间距。
4. 若用户需要 WPS/Word 点击正文 `[1]` 跳转文末参考文献，运行 `link-references`。该命令会给文末 `[n]` 条目插入 `w:bookmarkStart/w:bookmarkEnd`，并把正文 `[n]` 包装为 `w:hyperlink w:anchor="ref_n"` 内部超链接。
5. 最后运行 `verify`。带 `--visual` 时使用 Word COM 导出 PDF，并用 `pypdfium2` 渲染页面；为避免隐藏弹窗卡死，真正启动 Word 前需设置 `THESIS_ASSISTANT_ENABLE_WORD_COM_VISUAL=1`，缺少依赖时必须报告失败原因，不得声称完成视觉检查。
6. 若要完整执行，用 `pipeline` 串起模板画像、修正前审查、保守修正和二次验证。

## 交付前检查

1. 是否联网核验格式规范、文献、数据集和图件标准。
2. 是否保留或说明模板优先规则。
3. 是否有备份或可回滚副本。
4. 是否没有编造实验结果。
5. 是否引用真实、编号连续、正文文末一致。
6. 是否说明缺失依赖和降级路径。
7. 是否完成 docx 提取或打包后的二次验证。
8. 是否避免空泛 AI 式表达。
9. 完整项目论文是否通过 `validate_thesis_docx.py` 的字数、图表、引用顺序、题注和基础版式检查。
