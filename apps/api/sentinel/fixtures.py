from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures"


def load_snapshot(name: str = "mantle_demo_snapshot") -> dict[str, Any]:
    path = FIXTURE_DIR / f"{name}.json"
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

