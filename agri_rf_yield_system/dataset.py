from __future__ import annotations

import pandas as pd

from .config import NASA_PARAMETERS, PROCESSED_DIR, WORLD_BANK_INDICATORS
from .utils import normalize_name, require_file, utc_now, write_json


TARGET_COLUMN = "yield_hg_per_ha"
CAT_FEATURES = ["country_norm"]
NUMERIC_FEATURES = [
    "year",
    *[f"nasa_{parameter.lower()}" for parameter in NASA_PARAMETERS],
    *WORLD_BANK_INDICATORS.values(),
]


def build_dataset(min_rows: int = 120) -> dict:
    faostat_path = PROCESSED_DIR / "faostat_crop_records.csv"
    wb_path = PROCESSED_DIR / "world_bank_indicators.csv"
    nasa_path = PROCESSED_DIR / "nasa_power_annual.csv"
    require_file(faostat_path, "Run download-data first.")
    require_file(wb_path, "Run download-data first.")
    require_file(nasa_path, "Run download-data first.")

    fao = pd.read_csv(faostat_path)
    fao["year"] = pd.to_numeric(fao["Year"], errors="coerce")
    fao["value"] = pd.to_numeric(fao["Value"], errors="coerce")
    fao["country_norm"] = fao["Area"].map(normalize_name)
    pivot = (
        fao.pivot_table(
            index=["country_norm", "Area", "year"],
            columns="Element",
            values="value",
            aggfunc="mean",
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )
    if "Yield" not in pivot.columns:
        raise RuntimeError("FAOSTAT processed records contain no Yield element.")
    pivot = pivot.rename(columns={"Area": "faostat_area", "Yield": TARGET_COLUMN})
    target = pivot[["country_norm", "faostat_area", "year", TARGET_COLUMN]].copy()

    wb = pd.read_csv(wb_path)
    nasa = pd.read_csv(nasa_path)
    merged = target.merge(wb, on=["country_norm", "year"], how="inner", suffixes=("", "_wb"))
    merged = merged.merge(nasa, on=["country_norm", "year"], how="inner", suffixes=("", "_nasa"))
    merged[TARGET_COLUMN] = pd.to_numeric(merged[TARGET_COLUMN], errors="coerce")
    for column in NUMERIC_FEATURES:
        if column in merged.columns:
            merged[column] = pd.to_numeric(merged[column], errors="coerce")

    feature_columns = CAT_FEATURES + [col for col in NUMERIC_FEATURES if col in merged.columns]
    before_drop = len(merged)
    selected_columns = []
    for column in ["country_norm", "faostat_area", "year", TARGET_COLUMN] + feature_columns:
        if column not in selected_columns:
            selected_columns.append(column)
    model_data = merged[selected_columns].copy()
    model_data = model_data.dropna(subset=[TARGET_COLUMN])
    non_null_features = model_data[feature_columns].notna().sum(axis=1)
    model_data = model_data[non_null_features >= max(3, len(feature_columns) // 2)]
    if len(model_data) < min_rows:
        raise RuntimeError(
            f"Dataset has {len(model_data)} usable rows after merge; minimum is {min_rows}. "
            "Check API downloads, date range, and country matching."
        )

    dataset_path = PROCESSED_DIR / "model_dataset.csv"
    model_data.to_csv(dataset_path, index=False, encoding="utf-8-sig")
    profile = {
        "created_at": utc_now(),
        "dataset_path": str(dataset_path),
        "rows_before_drop": int(before_drop),
        "rows": int(len(model_data)),
        "countries": int(model_data["country_norm"].nunique()),
        "year_min": int(model_data["year"].min()),
        "year_max": int(model_data["year"].max()),
        "target": TARGET_COLUMN,
        "features": feature_columns,
        "leakage_policy": "FAOSTAT production and harvested area are retained in source records but excluded from model features by default.",
        "missing_values": model_data[feature_columns + [TARGET_COLUMN]].isna().sum().to_dict(),
    }
    write_json(PROCESSED_DIR / "dataset_profile.json", profile)
    return profile
