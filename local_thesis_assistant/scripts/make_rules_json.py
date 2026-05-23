from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))

from local_thesis_assistant.thesis_assistant.rules import default_rules, save_rules


def main() -> None:
    save_rules(default_rules(), ROOT / "data" / "rules" / "default_rules.json")


if __name__ == "__main__":
    main()
