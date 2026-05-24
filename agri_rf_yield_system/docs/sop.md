# 从数据到论文的 SOP

## 1. 下载真实数据

先运行静态检查：

```powershell
python -m agri_rf_yield_system.scripts.smoke_check
```

```powershell
python -m agri_rf_yield_system download-data --crop "Maize (corn)" --start-year 2000 --end-year 2023 --max-countries 40
```

验收：

- `data/raw/download_manifest.json` 存在。
- manifest 中包含 FAOSTAT、NASA POWER、World Bank API 的 URL、时间和记录数。
- 命令失败时不得手写 CSV 顶替。

## 2. 构建建模数据集

```powershell
python -m agri_rf_yield_system build-dataset
```

验收：

- `data/processed/model_dataset.csv` 存在。
- `data/processed/dataset_profile.json` 记录样本数、年份范围、国家数量和特征列。
- `Production`、`Area harvested` 不作为默认特征，避免目标泄漏。

## 3. 训练随机森林

```powershell
python -m agri_rf_yield_system train --n-estimators 300 --test-years 5 --random-state 42
```

验收：

- `models/random_forest_yield.joblib` 存在。
- `models/metrics.json` 存在，正文实验指标只能引用该文件。
- `models/predictions.csv` 和 `models/feature_importance.csv` 存在。

## 4. 生成论文图表

```powershell
python -m agri_rf_yield_system evaluate
python -m agri_rf_yield_system export-thesis-assets
```

验收：

- `reports/figures/actual_vs_predicted.png`
- `reports/figures/residual_distribution.png`
- `reports/figures/feature_importance.png`
- `reports/thesis_assets/evidence_map.yaml`
- `reports/thesis_assets/experiment_report.md`

## 5. 运行系统并截图

```powershell
python -m agri_rf_yield_system run-app
```

按 `reports/thesis_assets/screenshot_checklist.md` 截图，放入论文对应章节。

## 6. 创建论文工作区

```powershell
python -m agri_rf_yield_system init-thesis
```

正式写正文前，把 `reports/thesis_assets/evidence_map.yaml` 合并到论文工作区证据链。没有真实运行指标时，只能写实验设计，不能写实验结论。
