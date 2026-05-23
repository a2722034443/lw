# 一期 DOCX 论文规范化助手调研依据

## 规则优先级

1. 学校模板或学院当年格式要求。本项目优先使用 `local_thesis_assistant/大连民族大学本科毕业设计说明书（论文）格式要求-2024.doc.doc`。
2. GB/T 7713.1-2025《信息与文献 编写规则 第1部分：学位论文》，用于论文结构、组成要素和编排基线。
3. GB/T 7714-2015《信息与文献 参考文献著录规则》，用于当前默认参考文献顺序编码制检查。
4. GB/T 7714-2025 预留为后续规则集，当前不作为默认规则。
5. ECMA-376 / ISO/IEC 29500 与 Microsoft Open XML 文档结构说明，用于 DOCX/WordprocessingML、段落、运行、表格、页眉页脚、域代码和公式对象的底层检查。
6. python-docx 官方文档，用于基础 DOCX 读取、段落、表格、图片、节、样式和页眉页脚处理。

## 已确认的工程结论

- `python-docx` 能创建和更新 `.docx`，适合基础段落、表格、图片、节和样式处理；但目录域、交叉引用域、OMML 公式、复杂页眉页脚和精确边框仍需读取或修改 OOXML。
- WordprocessingML 的正文由 `document/body/p/r/t` 等层级构成，格式信息分布在段落、运行、样式和文档部件中，不能只做纯文本检查。
- ECMA-376 是 Office Open XML 的标准来源，说明 DOCX 的词汇、文档表示和打包要求，应作为底层 XML 处理依据。
- 一期不直接自动改写事实内容、参考文献真实性和实验结论，只进行可逆格式修正，并把内容类问题写入报告。

## 外部来源

- 国家标准全文公开系统：GB/T 7713.1-2025 标准信息页。
- python-docx 1.2.0 documentation：https://python-docx.readthedocs.io/en/latest/
- Microsoft Learn：Structure of a WordprocessingML document。
- Ecma International：ECMA-376 Office Open XML file formats。
- Model Context Protocol：Tools specification。MCP 暂列二期，不进入一期实现范围。
