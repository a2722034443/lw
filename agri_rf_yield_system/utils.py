from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, data: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_name(value: str) -> str:
    text = value.lower().strip()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    aliases = {
        "united states of america": "united states",
        "china mainland": "china",
        "china hong kong sar": "hong kong sar china",
        "china macao sar": "macao sar china",
        "russian federation": "russia",
        "iran islamic republic of": "iran",
        "venezuela bolivarian republic of": "venezuela",
        "bolivia plurinational state of": "bolivia",
        "viet nam": "vietnam",
        "republic of korea": "korea rep",
        "democratic people s republic of korea": "korea dem people s rep",
        "united republic of tanzania": "tanzania",
        "egypt": "egypt arab rep",
        "czechia": "czech republic",
        "turkiye": "turkiye",
        "türkiye": "turkiye",
    }
    return aliases.get(text, text)


def require_file(path: Path, hint: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. {hint}")
