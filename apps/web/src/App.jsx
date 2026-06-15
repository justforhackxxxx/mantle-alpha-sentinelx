import React, { useMemo, useState } from "react";
import { Activity, BarChart3, Bot, ClipboardList, Database, ExternalLink, Radio, ShieldCheck, TrendingUp } from "lucide-react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const fallbackSignal = {
  signalId: "sig_demo",
  signalHash: "0x6f8d8ee21e5a7c34c6d49fb43e6a91bd0e4de6bb50b66ecf361d580a5d50f113",
  type: "smart_money_rotation",
  target: "mETH/MNT liquidity route",
  direction: "bullish",
  confidence: 0.76,
  horizon: "24h",
  thesis:
    "Tracked Mantle smart-money wallets are clustering around mETH/MNT activity while protocol flow is above baseline. The agent treats this as a short-term capital rotation signal, not as trading advice.",
  evidence: [
    { label: "smart wallets active", value: 7, source: "fixture.smartMoneyCohort" },
    { label: "cohort activity vs baseline", value: "2.4x", source: "fixture.rotationDetector" },
    { label: "protocol flow anomaly score", value: 82, source: "fixture.protocolFlow" },
    { label: "primary route", value: "mETH/MNT", source: "fixture.dexRoutes" }
  ],
  prediction: {
    metric: "relative swap volume",
    baseline: 1,
    target: 1.18,
    window: "24h"
  },
  outcome: "pending"
};

const mantleSepolia = {
  chainId: "0x138b",
  chainName: "Mantle Sepolia Testnet",
  nativeCurrency: { name: "MNT", symbol: "MNT", decimals: 18 },
  rpcUrls: ["https://rpc.sepolia.mantle.xyz"],
  blockExplorerUrls: ["https://sepolia.mantlescan.xyz"]
};

const committedSignalTx = "0xf7d6c4b51eb42bafdbf9b79f7f630c621750346557cc37a597c0a63863ba5c51";

function formatEvidenceValue(value) {
  if (Array.isArray(value)) {
    return `${value.length} wallets`;
  }
  return String(value);
}

function getWalletProvider() {
  const candidates = [
    window.okxwallet,
    ...(window.ethereum?.providers ?? []),
    window.ethereum
  ].filter(Boolean);
  return (
    candidates.find((provider) => provider.isOkxWallet || provider.isOKExWallet || provider.isOKXWallet) ??
    candidates[0]
  );
}

function App() {
  const [scan, setScan] = useState(null);
  const [commitment, setCommitment] = useState(null);
  const [trackRecord, setTrackRecord] = useState(null);
  const [dataSource, setDataSource] = useState(null);
  const [walletStatus, setWalletStatus] = useState("");
  const [txHash, setTxHash] = useState("");
  const [loading, setLoading] = useState(false);
  const signals = scan?.signals?.length ? scan.signals : [fallbackSignal];
  const signal = signals[0];
  const confidence = useMemo(() => Math.round(signal.confidence * 100), [signal]);

  async function runScan() {
    setLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8787/api/alpha/scan", { method: "POST" });
      if (!response.ok) throw new Error("scan failed");
      setScan(await response.json());
      const sourceResponse = await fetch("http://127.0.0.1:8787/api/data/source-status");
      if (sourceResponse.ok) {
        setDataSource(await sourceResponse.json());
      }
      const liveProbeResponse = await fetch("http://127.0.0.1:8787/api/data/live-probe");
      if (liveProbeResponse.ok) {
        const liveProbe = await liveProbeResponse.json();
        setDataSource((current) => ({ ...(current ?? {}), liveProbe }));
      }
      const commitmentResponse = await fetch("http://127.0.0.1:8787/api/alpha/commitment-preview");
      if (commitmentResponse.ok) {
        setCommitment(await commitmentResponse.json());
      }
      const trackRecordResponse = await fetch("http://127.0.0.1:8787/api/alpha/track-record");
      if (trackRecordResponse.ok) {
        setTrackRecord(await trackRecordResponse.json());
      }
    } catch {
      setScan({
        runId: "run_local_fallback",
        status: "completed",
        timeline: [
          "loaded local demo signal",
          "scored protocol flow anomalies",
          "generated evidence-grounded alpha thesis",
          "prepared signal hash for Mantle commitment"
        ],
        signals: [fallbackSignal]
      });
      setCommitment(null);
      setTrackRecord(null);
      setDataSource(null);
    } finally {
      setLoading(false);
    }
  }

  async function ensureCommitment() {
    if (commitment) return commitment;
    const commitmentResponse = await fetch("http://127.0.0.1:8787/api/alpha/commitment-preview");
    if (!commitmentResponse.ok) throw new Error("commitment preview unavailable");
    const preview = await commitmentResponse.json();
    setCommitment(preview);
    return preview;
  }

  async function addMantleSepolia() {
    const provider = getWalletProvider();
    if (!provider) {
      setWalletStatus("No browser wallet was found.");
      return;
    }
    try {
      setWalletStatus("Requesting Mantle Sepolia in wallet...");
      await provider.request({
        method: "wallet_addEthereumChain",
        params: [mantleSepolia]
      });
      setWalletStatus("Mantle Sepolia is ready in your wallet.");
    } catch (error) {
      setWalletStatus(error?.message ?? "Could not add Mantle Sepolia.");
    }
  }

  async function commitSignal() {
    const provider = getWalletProvider();
    if (!provider) {
      setWalletStatus("No browser wallet was found.");
      return;
    }
    setWalletStatus("Requesting wallet connection...");
    setTxHash("");
    try {
      const preview = await ensureCommitment();
      const accounts = await provider.request({ method: "eth_requestAccounts" });
      const from = accounts[0];

      try {
        await provider.request({
          method: "wallet_switchEthereumChain",
          params: [{ chainId: mantleSepolia.chainId }]
        });
      } catch (switchError) {
        if (switchError.code !== 4902) throw switchError;
        await provider.request({
          method: "wallet_addEthereumChain",
          params: [mantleSepolia]
        });
      }

      setWalletStatus("Waiting for MetaMask confirmation...");
      const hash = await provider.request({
        method: "eth_sendTransaction",
        params: [
          {
            from,
            to: preview.contract.address,
            data: preview.calldata,
            value: "0x0",
            gas: "0x7a120",
            gasPrice: "0xba43cfaa0"
          }
        ]
      });
      setTxHash(hash);
      setWalletStatus("Signal commitment submitted.");
    } catch (error) {
      setWalletStatus(error?.message ?? "Transaction was not submitted.");
    }
  }

  return (
    <main>
      <section className="topbar">
        <div>
          <p className="eyebrow">AI Alpha & Data</p>
          <h1>Mantle Alpha Sentinel</h1>
        </div>
        <button onClick={runScan} disabled={loading}>
          <Radio size={18} />
          {loading ? "Scanning" : "Run Alpha Scan"}
        </button>
      </section>

      <section className="layout">
        <div className="panel signal-panel">
          <div className="panel-header">
            <TrendingUp size={20} />
            <span>Top Alpha Signal</span>
          </div>
          <div className="signal-title">
            <h2>{signal.target}</h2>
            <span className={`badge ${signal.direction}`}>{signal.direction}</span>
          </div>
          <p className="thesis">{signal.thesis}</p>
          <div className="metrics">
            <div>
              <span>Confidence</span>
              <strong>{confidence}%</strong>
            </div>
            <div>
              <span>Horizon</span>
              <strong>{signal.horizon}</strong>
            </div>
            <div>
              <span>Outcome</span>
              <strong>{signal.outcome}</strong>
            </div>
          </div>
          <div className="hash">
            <span>Signal hash</span>
            <code>{signal.signalHash}</code>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <Bot size={20} />
            <span>Agent Timeline</span>
          </div>
          <ol className="timeline">
            {(scan?.timeline ?? [
              "waiting for scan trigger",
              "ready to observe Mantle smart-money flows",
              "ready to commit signal hash"
            ]).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ol>
        </div>
      </section>

      <section className="layout lower">
        <div className="panel">
          <div className="panel-header">
            <Activity size={20} />
            <span>Evidence</span>
          </div>
          <div className="evidence-list">
            {signal.evidence.map((item) => (
              <div className="evidence" key={item.label}>
                <span>{item.label}</span>
                <strong>{formatEvidenceValue(item.value)}</strong>
                <small>{item.source}</small>
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <ShieldCheck size={20} />
            <span>Benchmark Commitment</span>
          </div>
          <p className="compact">
            The signal is ready to be committed to `SignalRegistry` on Mantle Sepolia. Outcome resolution can later mark it as hit, miss, or invalid.
          </p>
          <div className="prediction">
            <span>{signal.prediction.metric}</span>
            <strong>{`${signal.prediction.baseline} -> ${signal.prediction.target}`}</strong>
            <small>{signal.prediction.window}</small>
          </div>
          {commitment && (
            <div className="commitment">
              <div>
                <span>Chain</span>
                <strong>{commitment.chain.name} · {commitment.chain.chainId}</strong>
              </div>
              <div>
                <span>Contract</span>
                <code>{commitment.contract.address}</code>
              </div>
              <div>
                <span>Method</span>
                <strong>{commitment.method.split("(")[0]}</strong>
              </div>
              <div>
                <span>Agent bytes32</span>
                <code>{commitment.args.agentIdBytes32}</code>
              </div>
              <div>
                <span>Calldata</span>
                <code>{commitment.calldata}</code>
              </div>
            </div>
          )}
          <div className="wallet-actions">
            <button className="secondary-button" onClick={addMantleSepolia}>
              Add Mantle
            </button>
            <button onClick={commitSignal}>
              <ShieldCheck size={18} />
              Commit Signal
            </button>
            <span>{walletStatus || "Uses MetaMask directly, without Remix."}</span>
          </div>
          <a className="tx-link" href={`https://sepolia.mantlescan.xyz/tx/${txHash || committedSignalTx}`} target="_blank" rel="noreferrer">
            <ExternalLink size={16} />
            {txHash ? "View commitment transaction" : "View verified Mantle proof"}
          </a>
          {commitment?.contract?.explorerUrl && (
            <a className="tx-link" href={commitment.contract.explorerUrl} target="_blank" rel="noreferrer">
              <ExternalLink size={16} />
              View SignalRegistry contract
            </a>
          )}
        </div>
      </section>

      {dataSource && (
        <section className="queue">
          <div className="panel">
            <div className="panel-header">
              <Database size={20} />
              <span>Data Source</span>
            </div>
            <div className="source-grid">
              <div>
                <span>Mode</span>
                <strong>{dataSource.mode}</strong>
              </div>
              <div>
                <span>Availability</span>
                <strong>{dataSource.available ? "available" : "fallback"}</strong>
              </div>
              <div>
                <span>Live ready</span>
                <strong>{dataSource.liveReady ? "yes" : "no"}</strong>
              </div>
            </div>
            <p className="compact">{dataSource.label}</p>
            {dataSource.liveProbe?.rpcProbe && (
              <div className="source-grid live-grid">
                <div>
                  <span>RPC chain</span>
                  <strong>{dataSource.liveProbe.rpcProbe.chainId ?? "n/a"}</strong>
                </div>
                <div>
                  <span>Latest block</span>
                  <strong>{dataSource.liveProbe.rpcProbe.latestBlock ?? "n/a"}</strong>
                </div>
                <div>
                  <span>RPC latency</span>
                  <strong>{dataSource.liveProbe.rpcProbe.latencyMs ?? "n/a"}ms</strong>
                </div>
              </div>
            )}
            {!!dataSource.limitations?.length && (
              <ul className="limitation-list">
                {dataSource.limitations.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            )}
          </div>
        </section>
      )}

      <section className="queue">
        <div className="panel">
          <div className="panel-header">
            <ClipboardList size={20} />
            <span>Signal Queue</span>
          </div>
          <div className="signal-list">
            {signals.map((item) => (
              <article className="signal-row" key={item.signalHash}>
                <div>
                  <strong>{item.target}</strong>
                  <span>{item.type.replaceAll("_", " ")}</span>
                </div>
                <div>
                  <strong>{Math.round(item.confidence * 100)}%</strong>
                  <span>{item.horizon}</span>
                </div>
                <code>{item.signalHash}</code>
              </article>
            ))}
          </div>
        </div>
      </section>

      {trackRecord && (
        <section className="queue">
          <div className="panel">
            <div className="panel-header">
              <BarChart3 size={20} />
              <span>Agent Track Record</span>
            </div>
            <div className="record-grid">
              <div>
                <span>Hit rate</span>
                <strong>{Math.round(trackRecord.hitRate * 100)}%</strong>
              </div>
              <div>
                <span>Hits</span>
                <strong>{trackRecord.hits}</strong>
              </div>
              <div>
                <span>Misses</span>
                <strong>{trackRecord.misses}</strong>
              </div>
              <div>
                <span>Pending</span>
                <strong>{trackRecord.pendingSignals}</strong>
              </div>
            </div>
            <div className="outcome-list">
              {trackRecord.outcomes.map((item) => (
                <article className="outcome-row" key={item.signalHash}>
                  <div>
                    <strong>{item.target}</strong>
                    <span>{item.prediction.metric}</span>
                  </div>
                  <div>
                    <strong>{item.observed ?? "pending"}</strong>
                    <span>{`${item.prediction.baseline} -> ${item.prediction.target}`}</span>
                  </div>
                  <span className={`outcome ${item.outcome}`}>{item.outcome}</span>
                </article>
              ))}
            </div>
          </div>
        </section>
      )}
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
