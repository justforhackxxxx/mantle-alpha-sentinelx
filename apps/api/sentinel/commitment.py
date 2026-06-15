from __future__ import annotations

import os
from typing import Any

from .abi import bytes32_from_text, encode_record_signal_calldata


DEFAULT_SIGNAL_REGISTRY_CONTRACT = "0x0000000000000000000000000000000000000000"


def signal_registry_address() -> str:
    return os.environ.get("SIGNAL_REGISTRY_ADDRESS", DEFAULT_SIGNAL_REGISTRY_CONTRACT)


def build_commitment_preview(signal: dict[str, Any]) -> dict[str, Any]:
    calldata = encode_record_signal_calldata(
        signal_hash=signal["signalHash"],
        agent_id=signal["agentId"],
        signal_type=signal["type"],
        target=signal["target"],
        horizon=signal["horizon"],
    )
    return {
        "chain": {
            "name": "Mantle Sepolia",
            "chainId": 5003,
        },
        "contract": {
            "name": "SignalRegistry",
            "address": signal_registry_address(),
            "status": "configured" if signal_registry_address() != DEFAULT_SIGNAL_REGISTRY_CONTRACT else "deployment_pending",
            "explorerUrl": f"https://sepolia.mantlescan.xyz/address/{signal_registry_address()}"
            if signal_registry_address() != DEFAULT_SIGNAL_REGISTRY_CONTRACT
            else None,
        },
        "method": "recordSignal(bytes32 signalHash, bytes32 agentId, string signalType, string target, string horizon)",
        "args": {
            "signalHash": signal["signalHash"],
            "agentId": signal["agentId"],
            "agentIdBytes32": "0x" + bytes32_from_text(signal["agentId"]),
            "signalType": signal["type"],
            "target": signal["target"],
            "horizon": signal["horizon"],
        },
        "calldata": calldata,
        "note": "Calldata is generated locally for the demo. A wallet or deployment script still needs to sign and broadcast the transaction.",
    }


def registry_status() -> dict[str, Any]:
    address = signal_registry_address()
    configured = address != DEFAULT_SIGNAL_REGISTRY_CONTRACT
    return {
        "chain": {
            "name": "Mantle Sepolia",
            "chainId": 5003,
        },
        "contract": {
            "name": "SignalRegistry",
            "address": address,
            "configured": configured,
            "explorerUrl": f"https://sepolia.mantlescan.xyz/address/{address}" if configured else None,
        },
        "nextStep": "Run make deploy, then set SIGNAL_REGISTRY_ADDRESS in .env."
        if not configured
        else "Use commitment calldata or wallet flow to record signal hashes.",
    }
