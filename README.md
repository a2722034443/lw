# 本地论文写作、DOCX 规范化与农业随机森林系统

当前仓库包含两部分：

- `local_thesis_assistant/`：论文写作 SOP、DOCX 审查、格式修正、参考文献跳转和验证工具。
- `agri_rf_yield_system/`：基于真实公开农业数据的随机森林作物产量预测与可视化系统。
- `skills/`：面向论文选题、文献、证据链、章节写作、质量审查和 DOCX 交付的本地 SOP Skills。

## 安装依赖

```powershell
pip install -r requirements.txt
```

## 农业随机森林系统

标准流程：

```powershell
python -m agri_rf_yield_system download-data --crop "Maize (corn)" --start-year 2000 --end-year 2023 --max-countries 40
python -m agri_rf_yield_system build-dataset
python -m agri_rf_yield_system train
python -m agri_rf_yield_system evaluate
python -m agri_rf_yield_system export-thesis-assets
python -m agri_rf_yield_system init-thesis
python -m agri_rf_yield_system run-app
```

系统不会内置或伪造农业数据。下载失败时命令失败，论文指标只允许来自真实运行生成的 `models/metrics.json`。

## 论文助手

```powershell
python -m local_thesis_assistant.thesis_flow init --title "你的论文题目" --type software-project --workspace local_thesis_assistant\outputs\my_thesis
python -m local_thesis_assistant.thesis_assistant audit local_thesis_assistant\data\samples\bad_sample.docx --md local_thesis_assistant\outputs\bad_audit.md
python -m local_thesis_assistant.thesis_assistant fix local_thesis_assistant\data\samples\bad_sample.docx local_thesis_assistant\outputs\bad_sample.fixed.docx
python -m local_thesis_assistant.thesis_assistant link-references thesis.docx thesis.linked.docx --json reference_links.json
python -m local_thesis_assistant.thesis_assistant verify local_thesis_assistant\outputs\bad_sample.fixed.docx --out-dir local_thesis_assistant\outputs\verify_bad
```

## 原则

- 正式文献、正式正文和实验结论必须联网核验，不能编造。
- 自动修正只处理可逆格式问题，不改事实内容和实验结果。
- 原始 DOCX 不覆盖，修正结果输出到新文件。
