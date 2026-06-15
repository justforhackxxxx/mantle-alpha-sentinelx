# Mantle Alpha Sentinel

Mantle Alpha Sentinel is an autonomous AI alpha analyst for Mantle. It detects smart-money capital rotation, explains why a signal matters, and records each prediction hash on-chain so the agent can build a public track record.

## Hackathon Fit

Primary track: AI Alpha & Data

Judge-facing submission copy is available in `docs/SUBMISSION.md`.

Mantle Alpha Sentinel focuses on:

- smart-money cohort tracking across Mantle wallets and protocols
- real Mantle RPC chain status probe for live-readiness
- protocol flow anomaly detection for swaps, liquidity, and yield assets
- AI-generated alpha explanations grounded in structured evidence
- on-chain signal benchmarking through a SignalRegistry contract
- Telegram or Discord-ready alpha alerts

## MVP Demo Flow

1. Run an alpha scan.
2. The agent observes wallet cohorts, protocol flow, and recent market context.
3. The signal engine detects a capital rotation or protocol-flow spike.
4. The AI explainer turns the evidence into a concise alpha thesis.
5. The app records a signal hash to Mantle Sepolia.
6. The dashboard shows signal history, status, and hit-rate-ready outcomes.

## On-chain Proof

- Network: Mantle Sepolia, chain id `5003`
- SignalRegistry: `0xB06b9AB4B9bD74Fdb45E6F0428ed0512C7B2Fb90`
- Registry explorer: https://sepolia.mantlescan.xyz/address/0xB06b9AB4B9bD74Fdb45E6F0428ed0512C7B2Fb90
- Signal commitment tx: https://sepolia.mantlescan.xyz/tx/0xf7d6c4b51eb42bafdbf9b79f7f630c621750346557cc37a597c0a63863ba5c51
- Signal hash: `0xb11162f187457f18423a1659d20ce689bbdb7a600c3aec3d4c082258907d0000`

## Repository Layout

```text
contracts/               SignalRegistry Solidity contract
docs/                    PRD, architecture, and demo script
apps/api/                Backend alpha-agent API
apps/web/                Frontend dashboard scaffold
packages/schemas/        Shared signal schema
```

## Local Development

Backend:

```bash
make api
```

Useful API routes:

```text
GET  /api/health
GET  /api/data/source-status
GET  /api/data/live-probe
POST /api/alpha/scan
GET  /api/alpha/signals
GET  /api/alpha/alert-preview
GET  /api/alpha/commitment-preview
GET  /api/alpha/track-record
GET  /api/onchain/registry-status
GET  /.well-known/agent-card.json
```

Frontend:

```bash
cd apps/web
npm install
cd ../..
make web
```

Contract work can start from `contracts/SignalRegistry.sol`.

Deployment notes are in `docs/DEPLOYMENT.md`.

Live data note:

The MVP uses deterministic fixture market snapshots for repeatable judging, and also probes real Mantle RPC through `/api/data/live-probe`. Set `MAS_DATA_MODE=live` plus `MANTLE_INDEXER_URL` when a production indexer is ready to map live protocol data into the detector schema.

Common commands:

```bash
make test
make build
make deploy
```
