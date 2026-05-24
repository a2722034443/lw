# 基于随机森林的多源农业数据作物产量预测系统

本项目服务于本科论文《基于随机森林的多源农业数据作物产量预测与可视化系统设计与实现》。

项目只使用可核验的公开数据源，不内置伪造数据。默认研究对象为玉米单产预测，数据来自 FAOSTAT、NASA POWER 和 World Bank API。所有下载数据、模型结果、图表和论文证据链都由命令生成。

## 安装

```powershell
pip install -r requirements.txt
```

## 标准流程

```powershell
python -m agri_rf_yield_system download-data --crop "Maize (corn)" --start-year 2000 --end-year 2023 --max-countries 40
python -m agri_rf_yield_system build-dataset
python -m agri_rf_yield_system train
python -m agri_rf_yield_system evaluate
python -m agri_rf_yield_system export-thesis-assets
python -m agri_rf_yield_system init-thesis
python -m agri_rf_yield_system run-app
```

## 输出目录

- `data/raw/`：原始下载文件和下载清单，不提交仓库。
- `data/processed/`：清洗后的 FAOSTAT、World Bank、NASA POWER 和建模数据集，不提交仓库。
- `models/`：训练后的模型、指标、预测结果和特征重要性，不提交仓库。
- `reports/figures/`：论文图表，不提交仓库。
- `reports/thesis_assets/`：论文证据链、实验报告、截图清单，不提交仓库。
- `thesis_workspace/`：由本地论文助手生成的论文写作工作区，不提交仓库。

## 不造假约束

- 下载失败时命令失败，不用 mock 数据替代。
- 论文指标只从 `models/metrics.json` 读取。
- 论文图表只从真实预测结果生成。
- 单条预测界面必须标记“仅基于已训练模型估计”。
