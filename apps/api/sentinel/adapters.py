from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol

from .fixtures import load_snapshot
from .rpc import probe_mantle_rpc


class SnapshotAdapter(Protocol):
    def load_market_snapshot(self) -> dict[str, Any]:
        ...

    def status(self) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class FixtureSnapshotAdapter:
    snapshot_name: str = "mantle_demo_snapshot"

    def load_market_snapshot(self) -> dict[str, Any]:
        snapshot = load_snapshot(self.snapshot_name)
        snapshot["dataSource"] = self.status()
        return snapshot

    def status(self) -> dict[str, Any]:
        return {
            "mode": "fixture",
            "label": "Deterministic Mantle demo snapshot",
            "available": True,
            "liveReady": False,
            "limitations": [
                "Uses curated fixture data for repeatable hackathon demo scans.",
                "Replace with LiveMantleAdapter once indexer and RPC credentials are configured.",
            ],
        }


@dataclass(frozen=True)
class LiveMantleAdapter:
    rpc_url: str | None = None
    indexer_url: str | None = None

    def load_market_snapshot(self) -> dict[str, Any]:
        if not self.has_rpc:
            snapshot = load_snapshot("mantle_demo_snapshot")
            snapshot["dataSource"] = self.status()
            return snapshot

        # MVP boundary: keep detector input stable while live indexer implementation lands.
        snapshot = load_snapshot("mantle_demo_snapshot")
        snapshot["dataSource"] = {
            **self.status(),
            "limitations": [
                "Live provider config detected; adapter currently falls back to demo snapshot shape.",
                "Next implementation step maps RPC/indexer responses into smartMoneyCohorts, protocolFlows, and yieldAssets.",
            ],
        }
        return snapshot

    @property
    def has_rpc(self) -> bool:
        return bool(self.rpc_url)

    @property
    def is_configured(self) -> bool:
        return bool(self.rpc_url and self.indexer_url)

    def status(self) -> dict[str, Any]:
        rpc_probe = probe_mantle_rpc(self.rpc_url) if self.rpc_url else {"ok": False, "error": "rpc_url_not_configured"}
        return {
            "mode": "live",
            "label": "Mantle live adapter",
            "available": bool(rpc_probe.get("ok")),
            "liveReady": self.is_configured,
            "rpcConfigured": bool(self.rpc_url),
            "indexerConfigured": bool(self.indexer_url),
            "rpcProbe": rpc_probe,
            "limitations": _live_limitations(self.is_configured, bool(rpc_probe.get("ok")), bool(self.indexer_url)),
        }


def adapter_from_env() -> SnapshotAdapter:
    mode = os.environ.get("MAS_DATA_MODE", "fixture").strip().lower()
    if mode == "live":
        return LiveMantleAdapter(
            rpc_url=os.environ.get("MANTLE_RPC_URL") or os.environ.get("MANTLE_SEPOLIA_RPC_URL"),
            indexer_url=os.environ.get("MANTLE_INDEXER_URL"),
        )
    return FixtureSnapshotAdapter()


def data_source_status() -> dict[str, Any]:
    return adapter_from_env().status()


def live_probe() -> dict[str, Any]:
    adapter = LiveMantleAdapter(
        rpc_url=os.environ.get("MANTLE_RPC_URL") or os.environ.get("MANTLE_SEPOLIA_RPC_URL") or "https://rpc.mantle.xyz",
        indexer_url=os.environ.get("MANTLE_INDEXER_URL"),
    )
    return adapter.status()


def _live_limitations(is_configured: bool, rpc_ok: bool, has_indexer: bool) -> list[str]:
    limitations: list[str] = []
    if not rpc_ok:
        limitations.append("Mantle RPC probe is unavailable; live chain status cannot be verified.")
    if not has_indexer:
        limitations.append("MANTLE_INDEXER_URL is not configured, so smart-money cohort snapshots use fixture fallback.")
    if is_configured:
        limitations.append("Live provider config detected; detector input mapping is the next implementation step.")
    return limitations
