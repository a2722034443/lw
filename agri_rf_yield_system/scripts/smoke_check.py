from __future__ import annotations

from agri_rf_yield_system.cli import build_parser
from agri_rf_yield_system.config import (
    FAOSTAT_BULK_URL,
    NASA_POWER_MONTHLY_URL,
    WORLD_BANK_API_BASE,
)
from agri_rf_yield_system.dataset import CAT_FEATURES, NUMERIC_FEATURES, TARGET_COLUMN


def main() -> int:
    parser = build_parser()
    commands = set(parser._subparsers._group_actions[0].choices.keys())
    expected = {
        "download-data",
        "build-dataset",
        "train",
        "evaluate",
        "export-thesis-assets",
        "init-thesis",
        "run-app",
    }
    missing = expected - commands
    if missing:
        raise AssertionError(f"Missing CLI commands: {sorted(missing)}")
    if TARGET_COLUMN in NUMERIC_FEATURES or TARGET_COLUMN in CAT_FEATURES:
        raise AssertionError("Target column must not be a feature.")
    if "Production" in NUMERIC_FEATURES or "Area harvested" in NUMERIC_FEATURES:
        raise AssertionError("Leakage-prone FAOSTAT columns must not be default features.")
    for url in [FAOSTAT_BULK_URL, NASA_POWER_MONTHLY_URL, WORLD_BANK_API_BASE]:
        if not url.startswith("https://"):
            raise AssertionError(f"Non-HTTPS source URL: {url}")
    print("smoke check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
