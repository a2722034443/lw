# 官方来源与核验入口

本项目的正式数据和论文证据只允许来自以下可核验来源：

- FAOSTAT：作物与畜产品生产统计。入口：https://www.fao.org/faostat/
- FAOSTAT bulk：`Production_Crops_Livestock_E_All_Data_(Normalized).zip`
- NASA POWER：月度气象参数 API，系统读取 `YYYY13` 年度汇总值。入口：https://power.larc.nasa.gov/
- World Bank API：国家元数据与农业相关指标。入口：https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information
- scikit-learn：`RandomForestRegressor` 官方文档。入口：https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html
- Streamlit：系统界面开发文档。入口：https://docs.streamlit.io/

论文写作时必须记录：

- 数据下载命令。
- 下载时间。
- 原始 URL。
- 处理脚本。
- 模型训练命令。
- 评价指标文件路径。
- 图表文件路径。
