from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from sentinel.env import load_project_env

load_project_env()

from sentinel import run_alpha_scan
from sentinel.agent import AGENT_ID
from sentinel.alerts import format_alert
from sentinel.commitment import build_commitment_preview, registry_status
from sentinel.adapters import data_source_status, live_probe
from sentinel.ledger import LEDGER


def agent_card() -> dict[str, Any]:
    return {
        "schemaVersion": "mantle-alpha-sentinel.agent_card.v1",
        "id": AGENT_ID,
        "name": "Mantle Alpha Sentinel",
        "description": "Autonomous AI alpha analyst that detects Mantle smart-money rotation and benchmarks signals on-chain.",
        "skills": [
            "detect_smart_money_rotation",
            "detect_protocol_flow_spike",
            "explain_alpha_signal",
            "prepare_signal_commitment",
            "format_alpha_alert",
        ],
        "safety": {
            "noCustody": True,
            "noAutoTrading": True,
            "signalsAreNotInvestmentAdvice": True,
        },
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self._send({"status": "ok", "service": AGENT_ID})
            return
        if self.path == "/api/data/source-status":
            self._send(data_source_status())
            return
        if self.path == "/api/data/live-probe":
            self._send(live_probe())
            return
        if self.path == "/api/alpha/signals":
            self._send(LEDGER.signals() or LEDGER.record_scan(run_alpha_scan())["signals"])
            return
        if self.path == "/api/alpha/track-record":
            self._send(LEDGER.track_record())
            return
        if self.path == "/api/alpha/alert-preview":
            signal = run_alpha_scan()["signals"][0]
            self._send(format_alert(signal))
            return
        if self.path == "/api/alpha/commitment-preview":
            signal = run_alpha_scan()["signals"][0]
            self._send(build_commitment_preview(signal))
            return
        if self.path == "/api/onchain/registry-status":
            self._send(registry_status())
            return
        if self.path == "/.well-known/agent-card.json":
            self._send(agent_card())
            return
        self._send({"error": "not_found", "path": self.path}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path == "/api/alpha/scan":
            self._send(LEDGER.record_scan(run_alpha_scan()))
            return
        self._send({"error": "not_found", "path": self.path}, HTTPStatus.NOT_FOUND)

    def _send(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8787), Handler)
    print("Mantle Alpha Sentinel API running at http://127.0.0.1:8787")
    server.serve_forever()


if __name__ == "__main__":
    main()
