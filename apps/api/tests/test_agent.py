from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sentinel import run_alpha_scan
from sentinel.alerts import format_alert
from sentinel.abi import encode_record_signal_calldata, keccak_256
from sentinel.adapters import FixtureSnapshotAdapter, LiveMantleAdapter
from sentinel.commitment import build_commitment_preview, registry_status
from sentinel.rpc import probe_mantle_rpc
from sentinel.outcomes import build_track_record, resolve_signal_outcome


class AlphaAgentTest(unittest.TestCase):
    def test_keccak_selector_matches_erc20_transfer(self) -> None:
        selector = keccak_256(b"transfer(address,uint256)").hex()[:8]

        self.assertEqual(selector, "a9059cbb")

    def test_scan_returns_ranked_signals(self) -> None:
        response = run_alpha_scan()

        self.assertEqual(response["agentId"], "mantle-alpha-sentinel")
        self.assertEqual(response["status"], "completed")
        self.assertEqual(response["dataSource"]["mode"], "fixture")
        self.assertGreaterEqual(len(response["signals"]), 3)
        confidences = [signal["confidence"] for signal in response["signals"]]
        self.assertEqual(confidences, sorted(confidences, reverse=True))

    def test_signals_have_commitment_hashes_and_evidence(self) -> None:
        response = run_alpha_scan()

        for signal in response["signals"]:
            self.assertRegex(signal["signalHash"], r"^0x[a-f0-9]{64}$")
            self.assertTrue(signal["evidence"])
            self.assertIn("prediction", signal)
            self.assertIn("commitment", signal)
            self.assertEqual(signal["outcome"], "pending")

    def test_alert_preview_contains_signal_hash(self) -> None:
        signal = run_alpha_scan()["signals"][0]
        alert = format_alert(signal)

        self.assertEqual(alert["channel"], "telegram_or_discord")
        self.assertIn(signal["signalHash"], alert["text"])
        self.assertIn(signal["target"], alert["text"])

    def test_commitment_preview_contains_record_signal_calldata(self) -> None:
        signal = run_alpha_scan()["signals"][0]
        preview = build_commitment_preview(signal)

        self.assertEqual(preview["chain"]["chainId"], 5003)
        self.assertEqual(preview["args"]["signalHash"], signal["signalHash"])
        self.assertRegex(preview["args"]["agentIdBytes32"], r"^0x[a-f0-9]{64}$")
        self.assertRegex(preview["calldata"], r"^0x[a-f0-9]+$")
        self.assertGreater(len(preview["calldata"]), 10 + 64 * 5)

    def test_commitment_preview_reads_contract_address_from_env(self) -> None:
        signal = run_alpha_scan()["signals"][0]

        with patch.dict("os.environ", {"SIGNAL_REGISTRY_ADDRESS": "0x1234567890123456789012345678901234567890"}):
            preview = build_commitment_preview(signal)

        self.assertEqual(preview["contract"]["address"], "0x1234567890123456789012345678901234567890")
        self.assertEqual(preview["contract"]["status"], "configured")

    def test_registry_status_adds_mantlescan_link_when_configured(self) -> None:
        with patch.dict("os.environ", {"SIGNAL_REGISTRY_ADDRESS": "0x1234567890123456789012345678901234567890"}):
            status = registry_status()

        self.assertTrue(status["contract"]["configured"])
        self.assertIn("sepolia.mantlescan.xyz/address/0x1234567890123456789012345678901234567890", status["contract"]["explorerUrl"])

    def test_record_signal_calldata_starts_with_method_selector(self) -> None:
        signal = run_alpha_scan()["signals"][0]
        calldata = encode_record_signal_calldata(
            signal_hash=signal["signalHash"],
            agent_id=signal["agentId"],
            signal_type=signal["type"],
            target=signal["target"],
            horizon=signal["horizon"],
        )

        self.assertEqual(calldata[:10], "0xb0ea9be1")

    def test_outcome_resolver_marks_hits_and_misses(self) -> None:
        signals = run_alpha_scan()["signals"]
        outcomes = [resolve_signal_outcome(signal) for signal in signals]

        self.assertEqual(outcomes[0]["outcome"], "hit")
        self.assertIn("miss", {outcome["outcome"] for outcome in outcomes})

    def test_track_record_summarizes_hit_rate(self) -> None:
        record = build_track_record(run_alpha_scan()["signals"])

        self.assertEqual(record["resolvedSignals"], 3)
        self.assertEqual(record["hits"], 2)
        self.assertEqual(record["misses"], 1)
        self.assertEqual(record["hitRate"], 0.667)

    def test_fixture_adapter_exposes_demo_status(self) -> None:
        adapter = FixtureSnapshotAdapter()
        snapshot = adapter.load_market_snapshot()

        self.assertEqual(snapshot["dataSource"]["mode"], "fixture")
        self.assertTrue(snapshot["dataSource"]["available"])
        self.assertFalse(snapshot["dataSource"]["liveReady"])

    def test_live_adapter_without_indexer_falls_back_cleanly(self) -> None:
        adapter = LiveMantleAdapter(rpc_url="https://rpc.example", indexer_url=None)
        with patch("sentinel.adapters.probe_mantle_rpc", return_value={"ok": True, "chainId": 5000, "latestBlock": 1}):
            snapshot = adapter.load_market_snapshot()

        self.assertEqual(snapshot["dataSource"]["mode"], "live")
        self.assertTrue(snapshot["dataSource"]["available"])
        self.assertIn("smartMoneyCohorts", snapshot)

    def test_live_adapter_configured_marks_live_ready(self) -> None:
        adapter = LiveMantleAdapter(rpc_url="https://rpc.example", indexer_url="https://indexer.example")

        with patch("sentinel.adapters.probe_mantle_rpc", return_value={"ok": True, "chainId": 5000, "latestBlock": 1}):
            self.assertTrue(adapter.status()["liveReady"])

    def test_rpc_probe_handles_missing_url(self) -> None:
        probe = probe_mantle_rpc(None)

        self.assertFalse(probe["ok"])
        self.assertEqual(probe["error"], "rpc_url_not_configured")


if __name__ == "__main__":
    unittest.main()
