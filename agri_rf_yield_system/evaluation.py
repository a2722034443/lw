from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .config import FIGURE_DIR, MODEL_DIR, ensure_dirs
from .dataset import TARGET_COLUMN
from .utils import require_file, utc_now, write_json


def evaluate_outputs() -> dict:
    ensure_dirs()
    pred_path = MODEL_DIR / "predictions.csv"
    imp_path = MODEL_DIR / "feature_importance.csv"
    require_file(pred_path, "Run train first.")
    require_file(imp_path, "Run train first.")
    predictions = pd.read_csv(pred_path)
    importance = pd.read_csv(imp_path).head(20)

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7, 6))
    plt.scatter(predictions[TARGET_COLUMN], predictions["prediction"], alpha=0.75)
    low = min(predictions[TARGET_COLUMN].min(), predictions["prediction"].min())
    high = max(predictions[TARGET_COLUMN].max(), predictions["prediction"].max())
    plt.plot([low, high], [low, high], color="black", linewidth=1)
    plt.xlabel("Actual yield (hg/ha)")
    plt.ylabel("Predicted yield (hg/ha)")
    plt.title("Actual vs predicted maize yield")
    plt.tight_layout()
    actual_pred = FIGURE_DIR / "actual_vs_predicted.png"
    plt.savefig(actual_pred, dpi=180)
    plt.close()

    plt.figure(figsize=(7, 5))
    plt.hist(predictions["residual"], bins=20, color="#4C78A8", edgecolor="white")
    plt.xlabel("Residual (actual - predicted)")
    plt.ylabel("Count")
    plt.title("Prediction residual distribution")
    plt.tight_layout()
    residual = FIGURE_DIR / "residual_distribution.png"
    plt.savefig(residual, dpi=180)
    plt.close()

    plt.figure(figsize=(8, 6))
    ordered = importance.sort_values("importance")
    plt.barh(ordered["feature"], ordered["importance"], color="#59A14F")
    plt.xlabel("Importance")
    plt.title("Random forest feature importance")
    plt.tight_layout()
    importance_fig = FIGURE_DIR / "feature_importance.png"
    plt.savefig(importance_fig, dpi=180)
    plt.close()

    report = {
        "created_at": utc_now(),
        "figures": {
            "actual_vs_predicted": str(actual_pred),
            "residual_distribution": str(residual),
            "feature_importance": str(importance_fig),
        },
        "prediction_rows": int(len(predictions)),
        "importance_rows": int(len(importance)),
    }
    write_json(FIGURE_DIR / "evaluation_report.json", report)
    return report
