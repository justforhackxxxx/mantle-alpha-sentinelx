from __future__ import annotations

from typing import Any


def explain_signal(candidate: dict[str, Any]) -> str:
    signal_type = candidate["type"]
    evidence = {item["label"]: item["value"] for item in candidate["evidence"]}

    if signal_type == "smart_money_rotation":
        return (
            f"{evidence['smart wallets active']} tracked smart-money wallets are active around "
            f"{candidate['target']}, with cohort activity at {evidence['cohort activity vs baseline']} "
            "of baseline. The agent treats this as a short-term capital rotation signal, not as trading advice."
        )

    if signal_type == "protocol_flow_spike":
        return (
            f"{candidate['target']} is showing a protocol-flow spike: volume is "
            f"{evidence['volume vs baseline']} and transaction count is {evidence['tx count vs baseline']} "
            f"around {evidence['dominant pool']}. The agent marks this for watchlist escalation."
        )

    if signal_type == "yield_asset_accumulation":
        return (
            f"Smart-wallet net flow into {candidate['target']} is {evidence['net flow vs baseline']} "
            f"of baseline across {evidence['unique wallets']} wallets. The agent flags a possible "
            "Mantle yield-asset accumulation pattern."
        )

    return "The agent found an evidence-backed Mantle alpha signal."

