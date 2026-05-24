from __future__ import annotations

import pandas as pd
import streamlit as st

from agri_rf_yield_system.config import FIGURE_DIR, MODEL_DIR, PROCESSED_DIR, RAW_DIR
from agri_rf_yield_system.dataset import CAT_FEATURES, NUMERIC_FEATURES, TARGET_COLUMN
from agri_rf_yield_system.modeling import load_metrics, load_model, train_model


st.set_page_config(page_title="农业产量预测系统", layout="wide")
st.title("基于随机森林的作物产量预测与可视化系统")

page = st.sidebar.radio(
    "功能",
    ["数据源管理", "模型训练", "预测结果", "特征重要性", "单条预测"],
)


def _read_csv(path):
    return pd.read_csv(path) if path.exists() else None


if page == "数据源管理":
    st.subheader("数据源与处理状态")
    manifest_path = RAW_DIR / "download_manifest.json"
    if manifest_path.exists():
        st.json(manifest_path.read_text(encoding="utf-8"))
    else:
        st.warning("尚未下载数据。请先运行 download-data。")
    dataset = _read_csv(PROCESSED_DIR / "model_dataset.csv")
    if dataset is not None:
        st.metric("建模数据行数", len(dataset))
        st.metric("国家/地区数量", dataset["country_norm"].nunique())
        st.dataframe(dataset.head(50), use_container_width=True)
        st.write("缺失值统计")
        st.dataframe(dataset.isna().sum().rename("missing").reset_index(), use_container_width=True)

elif page == "模型训练":
    st.subheader("随机森林训练")
    n_estimators = st.slider("n_estimators", 100, 800, 300, step=50)
    test_years = st.slider("测试集最近年份数", 3, 10, 5)
    st.caption("训练采用时间切分，较早年份训练，最近年份测试。")
    if st.button("开始训练"):
        try:
            metrics = train_model(n_estimators=n_estimators, test_years=test_years)
            st.success("训练完成")
            st.json(metrics)
        except Exception as exc:
            st.error(str(exc))

elif page == "预测结果":
    st.subheader("模型评价")
    try:
        st.json(load_metrics())
    except Exception as exc:
        st.warning(str(exc))
    predictions = _read_csv(MODEL_DIR / "predictions.csv")
    if predictions is not None:
        st.dataframe(predictions, use_container_width=True)
    for figure in ["actual_vs_predicted.png", "residual_distribution.png"]:
        path = FIGURE_DIR / figure
        if path.exists():
            st.image(str(path))

elif page == "特征重要性":
    st.subheader("随机森林特征重要性")
    importance = _read_csv(MODEL_DIR / "feature_importance.csv")
    if importance is None:
        st.warning("尚未训练模型。")
    else:
        st.dataframe(importance.head(30), use_container_width=True)
    path = FIGURE_DIR / "feature_importance.png"
    if path.exists():
        st.image(str(path))

elif page == "单条预测":
    st.subheader("单条产量预测")
    st.warning("预测值仅基于已训练模型估计，不能作为真实产量或政策结论。")
    dataset = _read_csv(PROCESSED_DIR / "model_dataset.csv")
    if dataset is None:
        st.info("请先构建数据集。")
    else:
        countries = sorted(dataset["country_norm"].dropna().unique())
        country = st.selectbox("国家/地区", countries)
        year = st.number_input("年份", min_value=1961, max_value=2100, value=int(dataset["year"].max()))
        latest = dataset[dataset["country_norm"].eq(country)].sort_values("year").tail(1)
        row = latest.iloc[0].to_dict() if not latest.empty else {}
        row["country_norm"] = country
        row["year"] = year
        for column in [col for col in NUMERIC_FEATURES if col != "year" and col in dataset.columns]:
            value = row.get(column)
            row[column] = st.number_input(column, value=float(value) if pd.notna(value) else 0.0)
        if st.button("预测"):
            try:
                model = load_model()
                features = CAT_FEATURES + [col for col in NUMERIC_FEATURES if col in dataset.columns]
                prediction = model.predict(pd.DataFrame([row])[features])[0]
                st.metric("预测单产 hg/ha", f"{prediction:.2f}")
            except Exception as exc:
                st.error(str(exc))
