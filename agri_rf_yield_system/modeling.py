from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .config import MODEL_DIR, PROCESSED_DIR, RANDOM_STATE, ensure_dirs
from .dataset import CAT_FEATURES, NUMERIC_FEATURES, TARGET_COLUMN
from .utils import require_file, utc_now, write_json


def _load_dataset() -> pd.DataFrame:
    path = PROCESSED_DIR / "model_dataset.csv"
    require_file(path, "Run build-dataset first.")
    data = pd.read_csv(path)
    data["year"] = pd.to_numeric(data["year"], errors="coerce")
    return data


def _feature_columns(data: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric = [column for column in NUMERIC_FEATURES if column in data.columns]
    categorical = [column for column in CAT_FEATURES if column in data.columns]
    return numeric, categorical


def _split_by_time(data: pd.DataFrame, test_years: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    years = sorted(int(year) for year in data["year"].dropna().unique())
    if len(years) <= test_years:
        raise RuntimeError(f"Not enough distinct years ({len(years)}) for test_years={test_years}.")
    split_year = years[-test_years]
    train = data[data["year"] < split_year].copy()
    test = data[data["year"] >= split_year].copy()
    if train.empty or test.empty:
        raise RuntimeError("Time split produced empty train or test data.")
    return train, test


def train_model(n_estimators: int = 300, test_years: int = 5, random_state: int = RANDOM_STATE) -> dict:
    ensure_dirs()
    data = _load_dataset()
    numeric, categorical = _feature_columns(data)
    train, test = _split_by_time(data, test_years)
    features = categorical + numeric

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical),
        ]
    )
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        random_state=random_state,
        n_jobs=-1,
        oob_score=True,
        bootstrap=True,
    )
    pipeline = Pipeline([("preprocessor", preprocessor), ("model", model)])
    pipeline.fit(train[features], train[TARGET_COLUMN])
    predictions = pipeline.predict(test[features])

    rmse = float(np.sqrt(mean_squared_error(test[TARGET_COLUMN], predictions)))
    metrics = {
        "created_at": utc_now(),
        "model": "RandomForestRegressor",
        "n_estimators": n_estimators,
        "random_state": random_state,
        "split": "time_based",
        "test_years": test_years,
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "train_year_min": int(train["year"].min()),
        "train_year_max": int(train["year"].max()),
        "test_year_min": int(test["year"].min()),
        "test_year_max": int(test["year"].max()),
        "mae": float(mean_absolute_error(test[TARGET_COLUMN], predictions)),
        "rmse": rmse,
        "r2": float(r2_score(test[TARGET_COLUMN], predictions)),
        "oob_score": float(getattr(pipeline.named_steps["model"], "oob_score_", float("nan"))),
        "target": TARGET_COLUMN,
        "features": features,
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_DIR / "random_forest_yield.joblib")
    write_json(MODEL_DIR / "metrics.json", metrics)
    pred = test[["country_norm", "faostat_area", "year", TARGET_COLUMN]].copy()
    pred["prediction"] = predictions
    pred["residual"] = pred[TARGET_COLUMN] - pred["prediction"]
    pred.to_csv(MODEL_DIR / "predictions.csv", index=False, encoding="utf-8-sig")

    names = pipeline.named_steps["preprocessor"].get_feature_names_out()
    importance = pd.DataFrame(
        {
            "feature": names,
            "importance": pipeline.named_steps["model"].feature_importances_,
        }
    ).sort_values("importance", ascending=False)
    importance.to_csv(MODEL_DIR / "feature_importance.csv", index=False, encoding="utf-8-sig")
    return metrics


def load_model() -> Pipeline:
    path = MODEL_DIR / "random_forest_yield.joblib"
    require_file(path, "Run train first.")
    return joblib.load(path)


def load_metrics() -> dict:
    path = MODEL_DIR / "metrics.json"
    require_file(path, "Run train first.")
    return json.loads(path.read_text(encoding="utf-8"))
