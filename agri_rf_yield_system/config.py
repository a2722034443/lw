from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODEL_DIR = PROJECT_ROOT / "models"
REPORT_DIR = PROJECT_ROOT / "reports"
FIGURE_DIR = REPORT_DIR / "figures"
THESIS_ASSET_DIR = REPORT_DIR / "thesis_assets"

FAOSTAT_BULK_URL = (
    "https://bulks-faostat.fao.org/production/"
    "Production_Crops_Livestock_E_All_Data_(Normalized).zip"
)
FAOSTAT_FALLBACK_URL = (
    "https://fenixservices.fao.org/faostat/static/bulkdownloads/"
    "Production_Crops_Livestock_E_All_Data_(Normalized).zip"
)

NASA_POWER_MONTHLY_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"
WORLD_BANK_API_BASE = "https://api.worldbank.org/v2"

DEFAULT_CROP = "Maize (corn)"
DEFAULT_START_YEAR = 2000
DEFAULT_END_YEAR = 2023
DEFAULT_MAX_COUNTRIES = 40
RANDOM_STATE = 42

NASA_PARAMETERS = [
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "PRECTOTCORR",
    "ALLSKY_SFC_SW_DWN",
]

WORLD_BANK_INDICATORS = {
    "AG.LND.AGRI.ZS": "agricultural_land_percent",
    "AG.LND.ARBL.ZS": "arable_land_percent",
    "SP.RUR.TOTL.ZS": "rural_population_percent",
    "NV.AGR.TOTL.ZS": "agriculture_value_added_percent_gdp",
}

SOURCE_URLS = {
    "FAOSTAT": "https://www.fao.org/faostat/",
    "FAOSTAT bulk": FAOSTAT_BULK_URL,
    "NASA POWER": "https://power.larc.nasa.gov/",
    "World Bank API": "https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information",
    "scikit-learn RandomForestRegressor": "https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html",
    "Streamlit": "https://docs.streamlit.io/",
}


def ensure_dirs() -> None:
    for path in [RAW_DIR, PROCESSED_DIR, MODEL_DIR, FIGURE_DIR, THESIS_ASSET_DIR]:
        path.mkdir(parents=True, exist_ok=True)
