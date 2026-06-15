from __future__ import annotations

from typing import Any

from .fixtures import load_snapshot


def resolve_signal_outcome(signal: dict[str, Any], outcome_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    snapshot = outcome_snapshot or load_snapshot("outcome_snapshot")
    prediction = signal["prediction"]
    metric = prediction["metric"]
    observed = snapshot["observations"].get(metric)

    if observed is None:
        status = "pending"
        delta = None
    else:
        target = prediction["target"]
        status = "hit" if observed >= target else "miss"
        delta = round(observed - target, 4)

    return {
        "signalId": signal["signalId"],
        "signalHash": signal["signalHash"],
        "type": signal["type"],
        "target": signal["target"],
        "prediction": prediction,
        "observed": observed,
        "outcome": status,
        "deltaToTarget": delta,
        "resolvedFrom": snapshot["snapshotId"],
    }


def build_track_record(signals: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes = [resolve_signal_outcome(signal) for signal in signals]
    resolved = [item for item in outcomes if item["outcome"] in {"hit", "miss"}]
    hits = [item for item in resolved if item["outcome"] == "hit"]
    misses = [item for item in resolved if item["outcome"] == "miss"]
    pending = [item for item in outcomes if item["outcome"] == "pending"]
    hit_rate = round(len(hits) / len(resolved), 3) if resolved else None

    return {
        "agentId": signals[0]["agentId"] if signals else "mantle-alpha-sentinel",
        "resolvedSignals": len(resolved),
        "pendingSignals": len(pending),
        "hits": len(hits),
        "misses": len(misses),
        "hitRate": hit_rate,
        "outcomes": outcomes,
    }

