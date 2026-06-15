from __future__ import annotations

import json
from hashlib import sha256
from typing import Any


def stable_hash(payload: dict[str, Any]) -> str:
    material = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "0x" + sha256(material.encode("utf-8")).hexdigest()

