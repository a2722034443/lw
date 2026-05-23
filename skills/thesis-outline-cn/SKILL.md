---
name: thesis-outline-cn
description: 软件项目类本科论文标准框架生成 SOP。用于根据学校模板、GB/T 7713.1-2025、文献和项目计划生成章节大纲、写作计划、图表计划和引用需求时触发。
---

# 论文框架 SOP

## 触发场景

- 用户已有题目，需要标准论文大纲。
- 用户需要知道每章写什么、多少字、需要哪些图表和引用。
- 用户提供学校模板或格式要求，需要转成论文框架。

## 输入要求

- `topic_brief.md/json`
- 学校模板画像或模板文件。
- 文献库初稿。
- 项目类型，第一版默认软件项目类。
- 字数、图表、参考文献数量要求。

## 强制联网

生成正式大纲前必须确认：

- 学校模板或格式要求。
- GB/T 7713.1-2025 论文组成和结构要求。
- GB/T 7714-2015 参考文献顺序编码要求。
- 同类软件项目论文常见章节结构。

## 输出文件

- `outline.yaml`
- `writing_plan.md`

`outline.yaml` 必须包含：

- 章节编号。
- 章节标题。
- 写作目标。
- 关键问题。
- 建议字数。
- 需要的文献数量。
- 需要的图表。
- 需要的项目证据或实验证据。
- 是否必须有正文引用。

## 默认章节

1. 摘要、Abstract。
2. 第1章 绪论。
3. 第2章 相关技术与理论基础。
4. 第3章 需求分析。
5. 第4章 系统总体设计。
6. 第5章 系统详细设计与实现。
7. 第6章 系统测试与实验分析。
8. 第7章 工程管理与社会责任。
9. 第8章 总结与展望。
10. 参考文献、致谢、附录。

## 禁止事项

- 不得用固定模板覆盖学校明确要求。
- 不得为凑字数安排无意义图表。
- 不得在大纲中承诺尚未实现的实验结果。
- 不得把参考文献放在正文之后再临时补。

## 操作步骤

1. 读取题目和选题评估。
2. 读取学校模板或通用规则。
3. 按软件项目论文闭环安排章节。
4. 给每一节写明“写作任务”和“证据来源”。
5. 生成图表清单：架构图、用例图、ER 图、流程图、测试表、实验结果表。
6. 生成引用需求：绪论和相关技术必须有文献，设计实现以项目证据为主。
7. 输出 `outline.yaml` 和 `writing_plan.md`。

## CLI 示例

```powershell
python -m local_thesis_assistant.thesis_flow build-outline --workspace local_thesis_assistant\outputs\flow_demo --profile local_thesis_assistant\outputs\template_profile.json --min-words 20000 --min-figures 40 --min-tables 6
```

## 交付前检查

- 每章都有写作目标。
- 每章都有证据来源要求。
- 图表数量和论文规模匹配。
- 章节之间形成“问题、方案、实现、验证、总结”闭环。

## 衔接顺序

上游：`topic-research-cn`、`literature-manager-cn`。  
下游：`project-design-cn`、`experiment-planner-cn`、`chapter-writer-cn`。
