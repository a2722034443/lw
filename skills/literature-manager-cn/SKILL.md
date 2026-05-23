---
name: literature-manager-cn
description: 中文本科论文文献检索、真实性核验、GB/T 7714 条目生成和正文引用规划 SOP。用于用户需要真实参考文献、文献综述、引用编号、参考文献库或文献核验时触发。
---

# 文献管理 SOP

## 触发场景

- 需要为论文题目检索真实文献。
- 需要生成 GB/T 7714-2015 顺序编码参考文献。
- 需要判断某条参考文献是否真实、是否适合引用。
- 需要把文献映射到绪论、相关技术、需求、实验等章节。

## 输入要求

- 论文题目或主题关键词。
- 论文类型，第一版默认软件项目类本科论文。
- 最少文献数量，默认不少于 15 条，用户要求优先。
- 年份窗口，默认近 5 年优先，但基础经典文献可保留。
- 中英文比例、期刊/会议/学位论文要求，如无要求按学校模板和导师要求。

## 强制联网

正式文献条目必须能从可信来源核验：

- DOI resolver、出版社页面、期刊官网。
- CNKI、万方、维普等数据库页面。
- Google Scholar、Semantic Scholar、DBLP、ACM、IEEE、Springer、Elsevier 等。
- 标准、官方文档、项目官方文档。

无法核验的条目只能放入“候选文献”，不能进入正式参考文献。

## 输出文件

在工作区生成或更新：

- `literature/library.csv`
- `literature/references_gbt7714.md`
- `literature/verification.md`
- `literature/research_queries.md`

`library.csv` 字段固定为：

- `id`
- `title`
- `authors`
- `year`
- `source`
- `type`
- `doi`
- `url`
- `verified`
- `used_in_chapter`
- `key_point`
- `gbt7714`

## 禁止事项

- 不得凭记忆补 DOI、卷期、页码。
- 不得把 arXiv 预印本伪装成期刊论文。
- 不得把 GitHub README 写成学术论文。
- 不得生成文末有但正文不引用的正式参考文献。
- 不得让正文引用顺序和文末编号不一致。

## 操作步骤

1. 生成中文和英文检索式。
2. 联网检索并记录来源 URL。
3. 筛选文献：相关性、年份、类型、可信度、可用于哪一章。
4. 为每条文献提炼一句“支撑点”。
5. 按正文首次使用顺序编号。
6. 生成 GB/T 7714-2015 条目。
7. 输出核验表，标明保留、候选、删除。
8. 调用现有 `validate_gbt_references.py` 做基础格式检查。

## CLI 示例

```powershell
python -m local_thesis_assistant.thesis_flow research-literature --workspace local_thesis_assistant\outputs\flow_demo --topic "本地 DOCX 论文格式检查 自动修正" --min 20
python skills\thesis-docx-writer-cn\scripts\validate_gbt_references.py literature\references_gbt7714.md --body draft\thesis.md
```

## 交付前检查

- 每条正式文献都有可访问来源或 DOI。
- 每条正式文献都标记使用章节。
- 文献条目不含“待补页码”“未知期刊”等占位。
- 文献综述不是文献堆砌，而是按主题归类。
- 正文引用和文末编号可以由 `link-references` 继续处理。

## 衔接顺序

上游：`topic-research-cn`。  
下游：`thesis-outline-cn`、`evidence-writing-cn`、`chapter-writer-cn`。
