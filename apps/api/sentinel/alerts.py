from __future__ import annotations

from typing import Any


def format_alert(signal: dict[str, Any]) -> dict[str, str]:
    confidence = round(signal["confidence"] * 100)
    text = (
        f"Mantle Alpha Sentinel\n"
        f"{signal['direction'].upper()} | {signal['target']} | {confidence}% confidence\n\n"
        f"{signal['thesis']}\n\n"
        f"Prediction: {signal['prediction']['metric']} >= {signal['prediction']['target']} "
        f"within {signal['prediction']['window']}\n"
        f"Signal hash: {signal['signalHash']}"
    )
    return {
        "channel": "telegram_or_discord",
        "format": "plain_text",
        "text": text,
    }

