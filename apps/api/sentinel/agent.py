from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .adapters import SnapshotAdapter, adapter_from_env
from .detectors import detect_signals
from .explainer import explain_signal
from .hashing import stable_hash


AGENT_ID = "mantle-alpha-sentinel"


def build_signal(candidate: dict[str, Any], created_at: str) -> dict[str, Any]:
    commitment = {
        "agentId": AGENT_ID,
        "type": candidate["type"],
        "target": candidate["target"],
        "direction": candidate["direction"],
        "confidence": candidate["confidence"],
        "horizon": candidate["horizon"],
        "prediction": candidate["prediction"],
        "evidence": candidate["evidence"],
    }
    signal_hash = stable_hash(commitment)
    return {
        "signalId": f"sig_{signal_hash[2:10]}",
        "signalHash": signal_hash,
        "agentId": AGENT_ID,
        "type": candidate["type"],
        "target": candidate["target"],
        "direction": candidate["direction"],
        "confidence": candidate["confidence"],
        "horizon": candidate["horizon"],
        "thesis": explain_signal(candidate),
        "evidence": candidate["evidence"],
        "prediction": candidate["prediction"],
        "outcome": "pending",
        "createdAt": created_at,
        "commitment": commitment,
    }


def run_alpha_scan(adapter: SnapshotAdapter | None = None) -> dict[str, Any]:
    now = datetime.now(UTC)
    selected_adapter = adapter or adapter_from_env()
    snapshot = selected_adapter.load_market_snapshot()
    candidates = detect_signals(snapshot)
    signals = [build_signal(candidate, now.isoformat()) for candidate in candidates]
    return {
        "runId": f"run_{now.strftime('%Y%m%d%H%M%S')}",
        "agentId": AGENT_ID,
        "status": "completed" if signals else "no_signal",
        "snapshotId": snapshot["snapshotId"],
        "dataSource": snapshot.get("dataSource", selected_adapter.status()),
        "timeline": [
            "loaded Mantle market snapshot",
            "observed smart-money cohort activity",
            "scored protocol flow anomalies",
            "scored yield-asset accumulation",
            "generated evidence-grounded alpha thesis",
            "prepared signal hash for Mantle commitment",
        ],
        "signals": signals,
    }
