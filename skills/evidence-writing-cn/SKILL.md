---
name: evidence-writing-cn
description: 中文本科论文证据链写作 SOP。用于把正文段落与文献、项目设计、代码、实验结果、图表建立映射，防止空泛或无依据写作时触发。
---

# 证据链写作 SOP

## 触发场景

- 准备写正文前，需要整理每章依据。
- 已有草稿，需要检查每段是否有文献、项目或实验支撑。
- 用户担心论文“AI 味”或空泛。

## 输入要求

- `outline.yaml`
- `literature/library.csv`
- `project_spec.md`
- `experiment_log.csv`
- 图表清单。
- 章节草稿。

## 强制联网

证据链中的文献证据必须来自已联网核验的文献库。未核验文献不得作为正式证据。

## 输出文件

- `evidence_map.yaml`
- `evidence_gap_report.md`

`evidence_map.yaml` 每条记录包含：

- `section`
- `claim`
- `evidence_type`: literature/project/code/experiment/figure/table/analysis
- `source_id`
- `citation`
- `status`: verified/missing/draft

## 禁止事项

- 不得让关键结论没有证据。
- 不得把“分析判断”写成“实验结果”。
- 不得引用没有核验的文献。
- 不得让图表只出现但正文不解释。

## 操作步骤

1. 按章节列出关键论述。
2. 为每条论述绑定证据类型。
3. 缺证据的论述标记为 `missing`。
4. 写正文时用证据链控制语气：文献支持、系统实现、实验结果、作者分析要分清。
5. 写完后抽查每章至少 5 个关键段落。

## CLI 示例

```powershell
python -m local_thesis_assistant.thesis_flow write-section --workspace local_thesis_assistant\outputs\flow_demo --chapter 3 --evidence evidence_map.yaml
python -m local_thesis_assistant.thesis_flow review-draft --workspace local_thesis_assistant\outputs\flow_demo
```

## 交付前检查

- 绪论和相关技术有文献证据。
- 系统设计和实现有项目证据。
- 测试实验章节有实验日志证据。
- 结论不超过证据范围。

## 衔接顺序

上游：`literature-manager-cn`、`project-design-cn`、`experiment-planner-cn`。  
下游：`chapter-writer-cn`、`thesis-quality-review-cn`。
