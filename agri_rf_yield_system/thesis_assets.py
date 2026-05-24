from __future__ import annotations

import json
from pathlib import Path

from .config import (
    FIGURE_DIR,
    MODEL_DIR,
    RAW_DIR,
    SOURCE_URLS,
    THESIS_ASSET_DIR,
    ensure_dirs,
)
from .utils import read_json, utc_now


def _metrics_block() -> str:
    metrics_path = MODEL_DIR / "metrics.json"
    if not metrics_path.exists():
        return "模型尚未训练，论文不得写入实验结果。"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    return (
        f"- 训练集：{metrics['train_rows']} 条，年份 {metrics['train_year_min']}-{metrics['train_year_max']}\n"
        f"- 测试集：{metrics['test_rows']} 条，年份 {metrics['test_year_min']}-{metrics['test_year_max']}\n"
        f"- MAE：{metrics['mae']:.4f}\n"
        f"- RMSE：{metrics['rmse']:.4f}\n"
        f"- R2：{metrics['r2']:.4f}\n"
        f"- OOB score：{metrics['oob_score']:.4f}\n"
    )


def export_assets() -> Path:
    ensure_dirs()
    THESIS_ASSET_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = RAW_DIR / "download_manifest.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else {"sources": []}

    sources = "\n".join(
        f"- {name}: {url}" for name, url in SOURCE_URLS.items()
    )
    (THESIS_ASSET_DIR / "data_sources.md").write_text(
        f"""# 数据与工具来源

生成时间：{utc_now()}

## 官方入口

{sources}

## 本次下载记录

```json
{json.dumps(manifest, ensure_ascii=False, indent=2)}
```
""",
        encoding="utf-8",
    )

    figures = sorted(str(path) for path in FIGURE_DIR.glob("*.png"))
    (THESIS_ASSET_DIR / "experiment_report.md").write_text(
        f"""# 实验结果记录

生成时间：{utc_now()}

## 指标

{_metrics_block()}

## 图表

{chr(10).join(f"- {item}" for item in figures) if figures else "- 尚未生成图表。"}

## 论文写作约束

- 只能引用本文件记录的真实运行指标。
- 如果重新训练模型，必须同步更新本文件和论文正文。
- 不得把未运行的实验计划写成实验结果。
""",
        encoding="utf-8",
    )

    (THESIS_ASSET_DIR / "evidence_map.yaml").write_text(
        """evidence:
  data_sources:
    file: reports/thesis_assets/data_sources.md
    used_in: [chapter_01, chapter_03, chapter_06]
  experiment_results:
    file: reports/thesis_assets/experiment_report.md
    used_in: [chapter_06, abstract, conclusion]
  system_screenshots:
    file: reports/thesis_assets/screenshot_checklist.md
    used_in: [chapter_05]
  source_code:
    files:
      - agri_rf_yield_system/data_sources.py
      - agri_rf_yield_system/dataset.py
      - agri_rf_yield_system/modeling.py
      - agri_rf_yield_system/app.py
    used_in: [chapter_04, chapter_05]
""",
        encoding="utf-8",
    )

    (THESIS_ASSET_DIR / "screenshot_checklist.md").write_text(
        """# 系统截图清单

请运行 `python -m agri_rf_yield_system run-app` 后截图：

- 数据源管理页：显示 FAOSTAT、NASA POWER、World Bank 记录。
- 模型训练页：显示参数、训练/测试年份和训练按钮。
- 预测结果页：显示 MAE、RMSE、R2、真实值与预测值图。
- 特征重要性页：显示前 20 个特征。
- 单条预测页：显示“仅基于已训练模型估计”提示。
""",
        encoding="utf-8",
    )

    (THESIS_ASSET_DIR / "references_gbt7714_seed.md").write_text(
        """# 参考文献待核验清单

以下条目必须联网核验作者、题名、年份、来源页后再进入正式参考文献：

- FAO. FAOSTAT: Crops and livestock products[DB/OL].
- NASA. POWER Data Access Viewer and API[DB/OL].
- World Bank. World Bank API and agricultural indicators[DB/OL].
- Pedregosa F, Varoquaux G, Gramfort A, et al. Scikit-learn: Machine Learning in Python[J]. Journal of Machine Learning Research, 2011.
- Breiman L. Random forests[J]. Machine Learning, 2001.
""",
        encoding="utf-8",
    )
    return THESIS_ASSET_DIR
