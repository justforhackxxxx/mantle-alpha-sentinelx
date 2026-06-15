from __future__ import annotations

from typing import Any

from .agent import run_alpha_scan
from .outcomes import build_track_record


class InMemorySignalLedger:
    def __init__(self) -> None:
        self._signals: dict[str, dict[str, Any]] = {}

    def record_scan(self, scan: dict[str, Any]) -> dict[str, Any]:
        for signal in scan["signals"]:
            self._signals[signal["signalHash"]] = signal
        return scan

    def signals(self) -> list[dict[str, Any]]:
        return list(self._signals.values())

    def track_record(self) -> dict[str, Any]:
        if not self._signals:
            self.record_scan(run_alpha_scan())
        return build_track_record(self.signals())


LEDGER = InMemorySignalLedger()

