---
name: experiment-planner-cn
description: 软件项目类本科论文实验与测试设计 SOP。用于设计功能测试、性能测试、算法实验、对照实验、指标记录和实验章节写法时触发。
---

# 实验与测试 SOP

## 触发场景

- 需要写第6章测试与实验。
- 项目有算法、分类器、规则引擎、文档处理或系统性能要验证。
- 用户需要测试用例、指标、运行命令和结果记录表。

## 输入要求

- 项目设计文档。
- 可运行代码或待测试功能。
- 数据集或样本文档。
- 论文大纲中的第6章要求。

## 强制联网

如涉及第三方数据集、评价指标或模型，必须联网确认：

- 数据集来源、许可和字段。
- 指标定义。
- 对照方法或同类实验设置。
- 软件库版本和官方文档。

## 输出文件

- `experiment_plan.yaml`
- `experiment_log.csv`
- `test_cases.md`
- `result_tables.md`

内容必须包含：

- 实验目的。
- 实验环境。
- 数据来源。
- 测试用例。
- 指标。
- 运行命令。
- 预期输出。
- 实际结果记录位置。
- 失败条件。

## 禁止事项

- 不能运行实验时，不得写成“实验结果表明”。
- 不得编造准确率、召回率、耗时、样本数。
- 不得把一次手工观察写成完整性能测试。
- 不得忽略失败样例。

## 操作步骤

1. 区分功能测试、性能测试、算法实验和文档处理实验。
2. 为每类测试指定输入样本。
3. 写运行命令和随机种子。
4. 定义指标和通过标准。
5. 运行后把结果写入 `experiment_log.csv`。
6. 生成论文表格和图件需求。
7. 写实验章节时只引用真实日志。

## CLI 示例

```powershell
python -m local_thesis_assistant.thesis_flow plan-experiment --workspace local_thesis_assistant\outputs\flow_demo
```

## 交付前检查

- 每个实验结果能对应日志文件或命令输出。
- 每个指标有定义。
- 测试用例覆盖正常、异常和边界情况。
- 论文结论没有超出实验结果。

## 衔接顺序

上游：`project-design-cn`。  
下游：`evidence-writing-cn`、`chapter-writer-cn`、`thesis-quality-review-cn`。
