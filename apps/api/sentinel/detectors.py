from __future__ import annotations

from typing import Any


def detect_smart_money_rotation(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    cohort = snapshot["smartMoneyCohorts"][0]
    threshold = snapshot["thresholds"]["smartMoneyRotation"]
    active_wallets = [wallet for wallet in cohort["wallets"] if wallet["windowActions"] >= threshold["minActions"]]
    activity_ratio = cohort["windowActionTotal"] / max(cohort["baselineActionTotal"], 1)

    if len(active_wallets) < threshold["minWallets"] or activity_ratio < threshold["minActivityRatio"]:
        return None

    score = min(100, round((len(active_wallets) / threshold["minWallets"]) * 38 + activity_ratio * 22))
    confidence = min(0.92, round(0.48 + score / 250, 2))
    return {
        "type": "smart_money_rotation",
        "target": cohort["primaryRoute"],
        "direction": "bullish",
        "confidence": confidence,
        "horizon": "24h",
        "score": score,
        "evidence": [
            {"label": "smart wallets active", "value": len(active_wallets), "source": "fixture.smartMoneyCohort"},
            {"label": "cohort activity vs baseline", "value": f"{activity_ratio:.1f}x", "source": "fixture.rotationDetector"},
            {"label": "primary route", "value": cohort["primaryRoute"], "source": "fixture.dexRoutes"},
            {"label": "tracked wallets", "value": [wallet["label"] for wallet in active_wallets], "source": "fixture.smartMoneyCohort"},
        ],
        "prediction": {
            "metric": "relative swap volume",
            "baseline": 1.0,
            "target": 1.18,
            "window": "24h",
        },
    }


def detect_protocol_flow_spike(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    protocol = max(
        snapshot["protocolFlows"],
        key=lambda item: item["currentVolumeUsd"] / max(item["baselineVolumeUsd"], 1),
    )
    threshold = snapshot["thresholds"]["protocolFlowSpike"]
    volume_ratio = protocol["currentVolumeUsd"] / max(protocol["baselineVolumeUsd"], 1)
    tx_ratio = protocol["currentTxCount"] / max(protocol["baselineTxCount"], 1)

    if volume_ratio < threshold["minVolumeRatio"] or tx_ratio < threshold["minTxRatio"]:
        return None

    score = min(100, round(volume_ratio * 28 + tx_ratio * 18))
    confidence = min(0.9, round(0.44 + score / 260, 2))
    return {
        "type": "protocol_flow_spike",
        "target": protocol["name"],
        "direction": "watch",
        "confidence": confidence,
        "horizon": "12h",
        "score": score,
        "evidence": [
            {"label": "volume vs baseline", "value": f"{volume_ratio:.1f}x", "source": "fixture.protocolFlow"},
            {"label": "tx count vs baseline", "value": f"{tx_ratio:.1f}x", "source": "fixture.protocolFlow"},
            {"label": "dominant pool", "value": protocol["dominantPool"], "source": "fixture.protocolFlow"},
            {"label": "current volume usd", "value": protocol["currentVolumeUsd"], "source": "fixture.protocolFlow"},
        ],
        "prediction": {
            "metric": "pool activity persistence",
            "baseline": 1.0,
            "target": 1.12,
            "window": "12h",
        },
    }


def detect_yield_asset_accumulation(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    asset = max(snapshot["yieldAssets"], key=lambda item: item["smartWalletNetFlowUsd"])
    threshold = snapshot["thresholds"]["yieldAssetAccumulation"]
    flow_ratio = asset["smartWalletNetFlowUsd"] / max(asset["baselineNetFlowUsd"], 1)

    if asset["smartWalletNetFlowUsd"] < threshold["minNetFlowUsd"] or flow_ratio < threshold["minFlowRatio"]:
        return None

    score = min(100, round(flow_ratio * 24 + asset["uniqueWallets"] * 7))
    confidence = min(0.88, round(0.42 + score / 270, 2))
    return {
        "type": "yield_asset_accumulation",
        "target": asset["symbol"],
        "direction": "bullish",
        "confidence": confidence,
        "horizon": "48h",
        "score": score,
        "evidence": [
            {"label": "smart-wallet net flow usd", "value": asset["smartWalletNetFlowUsd"], "source": "fixture.yieldAssets"},
            {"label": "net flow vs baseline", "value": f"{flow_ratio:.1f}x", "source": "fixture.yieldDetector"},
            {"label": "unique wallets", "value": asset["uniqueWallets"], "source": "fixture.yieldAssets"},
            {"label": "related protocol", "value": asset["relatedProtocol"], "source": "fixture.yieldAssets"},
        ],
        "prediction": {
            "metric": "relative yield-asset flow",
            "baseline": 1.0,
            "target": 1.15,
            "window": "48h",
        },
    }


def detect_signals(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = [
        detect_smart_money_rotation(snapshot),
        detect_protocol_flow_spike(snapshot),
        detect_yield_asset_accumulation(snapshot),
    ]
    signals = [candidate for candidate in candidates if candidate is not None]
    return sorted(signals, key=lambda item: (item["confidence"], item["score"]), reverse=True)

