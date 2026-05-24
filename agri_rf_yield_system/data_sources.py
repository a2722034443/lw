from __future__ import annotations

import json
import time
import zipfile
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests

from .config import (
    FAOSTAT_BULK_URL,
    FAOSTAT_FALLBACK_URL,
    NASA_PARAMETERS,
    NASA_POWER_MONTHLY_URL,
    PROCESSED_DIR,
    RAW_DIR,
    WORLD_BANK_API_BASE,
    WORLD_BANK_INDICATORS,
    ensure_dirs,
)
from .utils import normalize_name, sha256_file, utc_now, write_json


def _download(url: str, output: Path, timeout: int = 120) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        with output.open("wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)
    return output


def _request_json(url: str, params: dict, timeout: int = 60) -> dict | list:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def download_faostat_crop(crop: str) -> dict:
    ensure_dirs()
    zip_path = RAW_DIR / "faostat_production_crops_livestock.zip"
    attempted = []
    for url in [FAOSTAT_BULK_URL, FAOSTAT_FALLBACK_URL]:
        attempted.append(url)
        try:
            _download(url, zip_path)
            source_url = url
            break
        except requests.RequestException:
            if zip_path.exists():
                zip_path.unlink()
    else:
        raise RuntimeError(f"FAOSTAT bulk download failed. Tried: {attempted}")

    filtered_path = PROCESSED_DIR / "faostat_crop_records.csv"
    wanted_elements = {"Yield", "Area harvested", "Production"}
    chunks: list[pd.DataFrame] = []
    with zipfile.ZipFile(zip_path) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if not csv_names:
            raise RuntimeError("FAOSTAT zip did not contain a CSV file.")
        with archive.open(csv_names[0]) as file:
            for chunk in pd.read_csv(file, chunksize=100_000, low_memory=False):
                if not {"Item", "Element", "Year", "Value", "Area"}.issubset(chunk.columns):
                    raise RuntimeError("FAOSTAT CSV schema is missing required columns.")
                item = chunk["Item"].astype(str).str.lower()
                crop_mask = item.eq(crop.lower()) | item.str.contains("maize", na=False)
                element_mask = chunk["Element"].astype(str).isin(wanted_elements)
                selected = chunk.loc[crop_mask & element_mask].copy()
                if not selected.empty:
                    selected["source_name"] = "FAOSTAT Crops and livestock products"
                    selected["source_url"] = source_url
                    selected["retrieved_at"] = utc_now()
                    selected["processing_script"] = "agri_rf_yield_system.data_sources.download_faostat_crop"
                    chunks.append(selected)

    if not chunks:
        raise RuntimeError(f"No FAOSTAT rows found for crop={crop!r}.")
    data = pd.concat(chunks, ignore_index=True)
    data.to_csv(filtered_path, index=False, encoding="utf-8-sig")
    return {
        "name": "FAOSTAT",
        "source_url": source_url,
        "raw_path": str(zip_path),
        "processed_path": str(filtered_path),
        "sha256": sha256_file(zip_path),
        "rows": int(len(data)),
        "retrieved_at": utc_now(),
    }


def download_world_bank(start_year: int, end_year: int) -> dict:
    ensure_dirs()
    countries_json = RAW_DIR / "world_bank_countries.json"
    payload = _request_json(
        f"{WORLD_BANK_API_BASE}/country",
        {"format": "json", "per_page": 400},
    )
    countries_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    records = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    countries = pd.DataFrame(records)
    countries = countries[countries["region"].apply(lambda item: item.get("id") != "NA")]
    countries = countries[["id", "iso2Code", "name", "longitude", "latitude"]].copy()
    countries["country_norm"] = countries["name"].map(normalize_name)
    countries["longitude"] = pd.to_numeric(countries["longitude"], errors="coerce")
    countries["latitude"] = pd.to_numeric(countries["latitude"], errors="coerce")
    countries.to_csv(PROCESSED_DIR / "world_bank_country_metadata.csv", index=False, encoding="utf-8-sig")

    frames: list[pd.DataFrame] = []
    for indicator, feature_name in WORLD_BANK_INDICATORS.items():
        url = f"{WORLD_BANK_API_BASE}/country/all/indicator/{indicator}"
        payload = _request_json(
            url,
            {"format": "json", "per_page": 20000, "date": f"{start_year}:{end_year}"},
        )
        rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        frame = pd.DataFrame(rows)
        if frame.empty:
            continue
        frame["country"] = frame["country"].apply(lambda item: item.get("value") if isinstance(item, dict) else None)
        frame["iso3"] = frame["countryiso3code"]
        frame["year"] = pd.to_numeric(frame["date"], errors="coerce")
        frame[feature_name] = pd.to_numeric(frame["value"], errors="coerce")
        frame["source_name"] = f"World Bank {indicator}"
        frame["source_url"] = url
        frame["retrieved_at"] = utc_now()
        frame["processing_script"] = "agri_rf_yield_system.data_sources.download_world_bank"
        frames.append(frame[["iso3", "country", "year", feature_name, "source_name", "source_url", "retrieved_at", "processing_script"]])
        time.sleep(0.2)

    if not frames:
        raise RuntimeError("World Bank API returned no indicator rows.")
    merged = None
    for frame in frames:
        value_cols = [col for col in frame.columns if col in WORLD_BANK_INDICATORS.values()]
        slim = frame[["iso3", "country", "year"] + value_cols].copy()
        merged = slim if merged is None else merged.merge(slim, on=["iso3", "country", "year"], how="outer")
    assert merged is not None
    merged["country_norm"] = merged["country"].map(normalize_name)
    merged["source_name"] = "World Bank API"
    merged["source_url"] = WORLD_BANK_API_BASE
    merged["retrieved_at"] = utc_now()
    merged["processing_script"] = "agri_rf_yield_system.data_sources.download_world_bank"
    indicators_path = PROCESSED_DIR / "world_bank_indicators.csv"
    merged.to_csv(indicators_path, index=False, encoding="utf-8-sig")
    return {
        "name": "World Bank API",
        "source_url": WORLD_BANK_API_BASE,
        "processed_path": str(indicators_path),
        "country_metadata_path": str(PROCESSED_DIR / "world_bank_country_metadata.csv"),
        "rows": int(len(merged)),
        "retrieved_at": utc_now(),
    }


def _top_countries_from_faostat(max_countries: int) -> pd.DataFrame:
    path = PROCESSED_DIR / "faostat_crop_records.csv"
    data = pd.read_csv(path)
    yield_rows = data[data["Element"].eq("Yield")].copy()
    yield_rows["country_norm"] = yield_rows["Area"].map(normalize_name)
    counts = yield_rows.groupby(["country_norm", "Area"], as_index=False).size()
    counts = counts.sort_values("size", ascending=False).head(max_countries)
    return counts


def _annual_value(values: dict, year: int):
    annual_key = f"{year}13"
    if annual_key in values:
        return values[annual_key]
    monthly = [values.get(f"{year}{month:02d}") for month in range(1, 13)]
    monthly = [value for value in monthly if value is not None]
    return sum(monthly) / len(monthly) if monthly else None


def download_nasa_power(start_year: int, end_year: int, max_countries: int) -> dict:
    ensure_dirs()
    top = _top_countries_from_faostat(max_countries)
    country_meta = pd.read_csv(PROCESSED_DIR / "world_bank_country_metadata.csv")
    selected = top.merge(country_meta, on="country_norm", how="inner")
    selected = selected.dropna(subset=["longitude", "latitude"]).head(max_countries)
    if selected.empty:
        raise RuntimeError("No country coordinates matched between FAOSTAT and World Bank metadata.")

    rows: list[dict] = []
    for _, country in selected.iterrows():
        params = {
            "parameters": ",".join(NASA_PARAMETERS),
            "community": "AG",
            "longitude": float(country["longitude"]),
            "latitude": float(country["latitude"]),
            "start": start_year,
            "end": end_year,
            "format": "JSON",
        }
        payload = _request_json(NASA_POWER_MONTHLY_URL, params, timeout=90)
        raw_path = RAW_DIR / "nasa_power" / f"{country['id']}_{start_year}_{end_year}.json"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        parameter_data = payload.get("properties", {}).get("parameter", {}) if isinstance(payload, dict) else {}
        for year in range(start_year, end_year + 1):
            record = {
                "iso3": country["id"],
                "country": country["name"],
                "country_norm": country["country_norm"],
                "year": year,
                "longitude": float(country["longitude"]),
                "latitude": float(country["latitude"]),
                "source_name": "NASA POWER Monthly Point API annual summary",
                "source_url": NASA_POWER_MONTHLY_URL,
                "retrieved_at": utc_now(),
                "processing_script": "agri_rf_yield_system.data_sources.download_nasa_power",
            }
            for parameter in NASA_PARAMETERS:
                values = parameter_data.get(parameter, {})
                record[f"nasa_{parameter.lower()}"] = _annual_value(values, year)
            rows.append(record)
        time.sleep(0.5)

    data = pd.DataFrame(rows)
    path = PROCESSED_DIR / "nasa_power_annual.csv"
    data.to_csv(path, index=False, encoding="utf-8-sig")
    return {
        "name": "NASA POWER",
        "source_url": NASA_POWER_MONTHLY_URL,
        "processed_path": str(path),
        "rows": int(len(data)),
        "countries": int(data["country_norm"].nunique()),
        "retrieved_at": utc_now(),
    }


def download_all(crop: str, start_year: int, end_year: int, max_countries: int) -> Path:
    manifest = {
        "created_at": utc_now(),
        "crop": crop,
        "start_year": start_year,
        "end_year": end_year,
        "max_countries": max_countries,
        "sources": [
            download_faostat_crop(crop),
            download_world_bank(start_year, end_year),
            download_nasa_power(start_year, end_year, max_countries),
        ],
    }
    return write_json(RAW_DIR / "download_manifest.json", manifest)
