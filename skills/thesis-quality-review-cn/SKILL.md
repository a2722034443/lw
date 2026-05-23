---
name: thesis-quality-review-cn
description: 中文本科论文内容质量审查 SOP。用于检查论文草稿是否空泛、AI 味、证据不足、章节不对应、图表未解释、引用缺失或实验结论无数据支撑时触发。
---

# 论文质量审查 SOP

## 触发场景

- 论文草稿写完或写完一章。
- 用户要求检查内容质量，不只是格式。
- 需要答辩前发现逻辑、证据、引用和图表问题。

## 输入要求

- `draft/thesis.md` 或 `chapters/*.md`
- `outline.yaml`
- `evidence_map.yaml`
- `literature/library.csv`
- `experiment_log.csv`
- DOCX 审查报告可选。

## 强制联网

如果审查发现文献或标准存疑，必须联网核验；不能凭记忆判断文献真假。

## 输出文件

- `review/content_review.md`
- `review/content_review.json`

报告分级：

- `error`：必须修改，如虚假结果、文献不存在、章节缺失。
- `warning`：建议修改，如表述空泛、引用不足、图表未解释。
- `info`：提示，如可以补充截图或测试用例。

## 审查维度

- 章节完整性。
- 章节之间是否对应。
- 每章是否有明确任务。
- 关键论述是否有证据。
- 文献是否真实可查。
- 图表是否被正文引用和解释。
- 实验结论是否来自日志。
- 是否存在 AI 味套话。
- 是否存在过度承诺。
- 是否有“待补”“这里写”等占位。

## 禁止事项

- 不得只说“整体不错”。
- 不得只查错别字而忽略证据。
- 不得替用户编造缺失实验。
- 不得把未核验文献标为通过。

## CLI 示例

```powershell
python -m local_thesis_assistant.thesis_flow review-draft --workspace local_thesis_assistant\outputs\flow_demo
```

## 交付前检查

- 所有 error 都有修改建议。
- 所有实验结论能追溯日志。
- 正文引用和文献库一致。
- DOCX 阶段还需调用 `thesis-docx-writer-cn` 的 `audit/fix/link-references/verify`。

## 衔接顺序

上游：`chapter-writer-cn`。  
下游：`thesis-docx-writer-cn`。
