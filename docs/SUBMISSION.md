# Mantle Alpha Sentinel Submission

## Project Title

Mantle Alpha Sentinel

## Track

AI Alpha & Data

## Short Description

Mantle Alpha Sentinel is an autonomous AI alpha analyst for Mantle. It detects smart-money rotations and protocol-flow anomalies, explains each signal with structured evidence, and commits prediction hashes on Mantle Sepolia so the agent can build a public, verifiable track record.

## Long Description

Mantle Alpha Sentinel helps users discover and evaluate emerging alpha in the Mantle ecosystem. The agent monitors smart-money wallet cohorts, protocol activity, and yield-asset flows, then turns anomaly detections into explainable alpha signals with confidence, horizon, evidence, and prediction metrics.

The project is designed for the AI Alpha & Data track. Instead of producing opaque market commentary, the agent creates accountable signals. Each signal is hashed and can be recorded on Mantle Sepolia through `SignalRegistry`, proving that the prediction existed before the outcome was known. The dashboard also includes track-record-ready outcome resolution so future versions can score the agent by hit rate, pending signals, and misses.

For the hackathon demo, the detector uses deterministic market snapshots for repeatable judging and also probes real Mantle RPC for live-readiness. The architecture can later connect to Mantle indexers, protocol APIs, DEX subgraphs, Telegram alerts, or Discord alpha feeds without changing the signal schema.

## Problem

Alpha signals in Web3 are often noisy, unverifiable, and hard to score after the fact. Traders see narratives after the move has already happened, and AI agents can make claims without being accountable for whether those claims worked.

## Solution

Mantle Alpha Sentinel combines deterministic anomaly detection, AI-style evidence explanation, and on-chain benchmarking:

- Detects smart-money cohort rotation, protocol-flow spikes, and yield-asset accumulation.
- Produces structured alpha signals with thesis, confidence, horizon, and evidence.
- Generates deterministic signal hashes.
- Commits signal hashes to Mantle Sepolia before outcomes are known.
- Tracks outcomes so agent performance can become measurable over time.

## Technical Highlights

- Frontend dashboard: React + Vite.
- Backend API: Python standard-library HTTP service.
- Signal engine: deterministic detectors for wallet cohorts, protocol flows, and yield assets.
- Data layer: repeatable fixture snapshots plus real Mantle RPC live probe.
- On-chain contract: Solidity `SignalRegistry`.
- Agent manifest: `/.well-known/agent-card.json`.
- Alert-ready output: Telegram or Discord payload preview.

## On-chain Proof

Network: Mantle Sepolia, chain id `5003`

SignalRegistry:

```text
0xB06b9AB4B9bD74Fdb45E6F0428ed0512C7B2Fb90
```

Registry explorer:

```text
https://sepolia.mantlescan.xyz/address/0xB06b9AB4B9bD74Fdb45E6F0428ed0512C7B2Fb90
```

Signal commitment transaction:

```text
https://sepolia.mantlescan.xyz/tx/0xf7d6c4b51eb42bafdbf9b79f7f630c621750346557cc37a597c0a63863ba5c51
```

Committed signal hash:

```text
0xb11162f187457f18423a1659d20ce689bbdb7a600c3aec3d4c082258907d0000
```

## Demo Flow

1. Open the dashboard.
2. Click `Run Alpha Scan`.
3. Show the top signal: `mETH/MNT liquidity route`.
4. Explain the evidence: smart wallets active, cohort activity above baseline, protocol flow anomaly score, and primary route.
5. Show the signal hash and Mantle Sepolia commitment preview.
6. Open the Mantlescan signal commitment transaction.
7. Show the track record panel and explain how outcomes can later score the agent.

## Video Script

Mantle Alpha Sentinel is an autonomous AI alpha analyst for the Mantle ecosystem.

In this demo, I run an alpha scan. The agent observes smart-money wallet cohorts, protocol flows, and yield-asset activity. It detects a smart-money rotation around the mETH/MNT liquidity route, assigns confidence, and explains the signal with structured evidence.

The key feature is accountability. The agent creates a deterministic signal hash and commits that hash to Mantle Sepolia through the SignalRegistry contract. This proves the signal existed before the outcome was known. Later, the outcome resolver can mark signals as hit, miss, or pending, creating a public track record for the agent.

This project fits the AI Alpha & Data track because it turns raw on-chain activity into explainable alpha and benchmarks the agent's performance on-chain.

## Suggested DoraHacks Tags

```text
Mantle, AI Agent, Alpha, On-chain Analytics, Smart Money, DeFi, Signal Benchmarking, Mantle Sepolia
```

## Local Run Commands

```bash
make api
cd apps/web
npm install
cd ../..
make web
```

Open:

```text
http://127.0.0.1:5174/
```

## Verification

```bash
make test
make build
```

Current result:

```text
14 API tests passed
frontend build passed
```
