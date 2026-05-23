---
name: chapter-writer-cn
description: 软件项目类本科论文分章正文写作 SOP。用于按证据链写摘要、绪论、相关技术、需求分析、系统设计、实现、测试实验、总结等章节时触发。
---

# 分章写作 SOP

## 触发场景

- 用户需要写某一章或整篇论文正文。
- 已有大纲、文献、项目设计和实验记录。
- 需要降低 AI 味，写得具体、可验证。

## 输入要求

- `outline.yaml`
- `evidence_map.yaml`
- `literature/library.csv`
- `project_spec.md`
- `experiment_log.csv`
- 目标章节编号。

## 强制联网

写正式章节前，涉及研究现状、技术介绍、标准、文献综述的部分必须联网核验来源。没有核验来源时，只能写草稿或待补说明。

## 输出文件

- `chapters/chapter_XX.md`
- 更新 `evidence_map.yaml`

每章必须包含：

- 章节目的。
- 与上一章/下一章的关系。
- 具体内容。
- 图表和引用位置。
- 小结。

## 章节写法

- 摘要：目的、方法、实现、结果、结论，不写空话。
- 绪论：背景、意义、研究现状、问题、研究内容、技术路线。
- 相关技术：只写项目实际用到的技术，并说明为什么用。
- 需求分析：用户、功能、非功能、用例、可行性。
- 总体设计：架构、模块、数据、接口、安全。
- 详细实现：核心模块、流程、关键算法、异常处理。
- 测试实验：环境、数据、用例、指标、结果、分析。
- 总结展望：完成工作、不足、后续改进。

## 禁止事项

- 不得写“具有重要意义”“显著提升”等无证据套话。
- 不得引用不存在的图表和实验。
- 不得把文献综述写成文献列表。
- 不得在测试章节写没有日志支撑的结果。

## CLI 示例

```powershell
python -m local_thesis_assistant.thesis_flow write-section --workspace local_thesis_assistant\outputs\flow_demo --chapter 3 --evidence evidence_map.yaml
```

## 交付前检查

- 章节内容和大纲一致。
- 关键论述都有证据链。
- 引用编号占位明确。
- 图表在正文中被解释。
- 没有“待补”“随便写”等占位进入最终稿。

## 衔接顺序

上游：`thesis-outline-cn`、`evidence-writing-cn`。  
下游：`thesis-quality-review-cn`、`thesis-docx-writer-cn`。
