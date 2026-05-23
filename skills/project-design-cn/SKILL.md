---
name: project-design-cn
description: 软件项目类本科毕设项目落地设计 SOP。用于把论文题目转成可实现系统，设计技术栈、功能模块、数据库、接口、页面、流程和测试点时触发。
---

# 项目设计 SOP

## 触发场景

- 题目已经确定，需要设计系统。
- 需要把论文中的需求分析、总体设计、详细实现写扎实。
- 需要图表清单、数据库表、接口和测试点。

## 输入要求

- 题目和选题评估。
- 论文大纲。
- 用户已有代码或计划使用的技术栈。
- 数据来源和系统运行环境。

## 强制联网

正式设计前应联网确认：

- 所选框架或库的官方文档。
- 同类系统的功能边界和常见模块。
- 图件类型的标准画法，复杂图调用 `diagram-norm-cn`。

## 输出文件

- `project_spec.md`
- `project_architecture.yaml`
- `figures_to_make.md`
- `test_points.md`

内容必须包含：

- 用户角色。
- 功能需求。
- 非功能需求。
- 模块划分。
- 数据结构或数据库设计。
- 接口设计。
- 页面或命令行流程。
- 安全、异常和日志策略。
- 需要生成的图。
- 可测试点。

## 禁止事项

- 不得设计一个无法在用户环境实现的系统。
- 不得把论文需求写成泛泛列表而没有模块承接。
- 不得把图件当装饰，图必须支持正文论证。
- 不得写不存在的页面截图或运行结果。

## 操作步骤

1. 从题目抽取系统名称和用户角色。
2. 写业务流程和使用场景。
3. 拆功能模块，模块要能对应代码或脚本。
4. 设计数据结构，说明来源和存储。
5. 设计接口或命令行入口。
6. 列出异常处理和边界条件。
7. 生成论文所需图表清单。
8. 生成测试点，交给 `experiment-planner-cn`。

## CLI 示例

```powershell
python -m local_thesis_assistant.thesis_flow design-project --workspace local_thesis_assistant\outputs\flow_demo
```

## 交付前检查

- 需求、设计、实现、测试能一一对应。
- 每个功能模块都有输入、处理、输出。
- 数据库或文件结构可被实现。
- 图件清单能交给 `diagram-norm-cn`。

## 衔接顺序

上游：`topic-research-cn`、`thesis-outline-cn`。  
下游：`experiment-planner-cn`、`chapter-writer-cn`、`diagram-norm-cn`。
