# 本地论文写作与 DOCX 规范化助手

这是一个面向“软件项目类本科毕业论文”的本地助手项目。当前仓库包含两层能力：

- `local_thesis_assistant.thesis_flow`：从题目到论文草稿的 SOP 工作流骨架，覆盖选题、标准调研、文献管理、项目设计、实验计划、证据链、章节写作、内容审查和 DOCX 导出。
- `local_thesis_assistant.thesis_assistant`：DOCX 读取、审查、保守修正、参考文献跳转链接和验证工具。

## 目录

- `local_thesis_assistant/`：Python 工具包、学校模板、规则和样例文档。
- `local_thesis_assistant/thesis_assistant/`：DOCX 审查与修正核心代码。
- `local_thesis_assistant/thesis_flow.py`：论文工作流 CLI。
- `local_thesis_assistant/data/rules/`：默认格式规则。
- `local_thesis_assistant/data/samples/`：可用于验证工具能力的好/坏 DOCX 样例。
- `skills/`：SOP 型本地 Skills，供后续按流程调用。

## 快速开始

安装依赖：

```powershell
pip install -r requirements.txt
```

```powershell
python -m local_thesis_assistant.thesis_flow init --title "你的论文题目" --type software-project --workspace local_thesis_assistant\outputs\my_thesis
python -m local_thesis_assistant.thesis_flow research-standards --workspace local_thesis_assistant\outputs\my_thesis --school 大连民族大学
python -m local_thesis_assistant.thesis_flow research-literature --workspace local_thesis_assistant\outputs\my_thesis --topic "你的论文关键词" --min 20
python -m local_thesis_assistant.thesis_flow build-outline --workspace local_thesis_assistant\outputs\my_thesis
python -m local_thesis_assistant.thesis_flow design-project --workspace local_thesis_assistant\outputs\my_thesis
python -m local_thesis_assistant.thesis_flow plan-experiment --workspace local_thesis_assistant\outputs\my_thesis
python -m local_thesis_assistant.thesis_flow write-section --workspace local_thesis_assistant\outputs\my_thesis --chapter 3 --evidence evidence_map.yaml
python -m local_thesis_assistant.thesis_flow review-draft --workspace local_thesis_assistant\outputs\my_thesis
python -m local_thesis_assistant.thesis_flow export-docx --workspace local_thesis_assistant\outputs\my_thesis --output local_thesis_assistant\outputs\my_thesis\draft\thesis.docx
```

DOCX 格式工具入口：

```powershell
python -m local_thesis_assistant.thesis_assistant diag
python -m local_thesis_assistant.thesis_assistant audit local_thesis_assistant\data\samples\bad_sample.docx --md local_thesis_assistant\outputs\bad_audit.md
python -m local_thesis_assistant.thesis_assistant fix local_thesis_assistant\data\samples\bad_sample.docx local_thesis_assistant\outputs\bad_sample.fixed.docx
python -m local_thesis_assistant.thesis_assistant link-references thesis.docx thesis.linked.docx --json reference_links.json
python -m local_thesis_assistant.thesis_assistant verify local_thesis_assistant\outputs\bad_sample.fixed.docx --out-dir local_thesis_assistant\outputs\verify_bad
```

## 原则

- 正式文献、正式正文和实验结论必须联网核验，不能编造。
- 自动修正只处理可逆的格式问题，不改事实内容和实验结果。
- 原始 DOCX 不覆盖，修正结果输出到新文件。
