# Product Requirements Document

## Product

Mantle Alpha Sentinel is an AI Alpha & Data agent that monitors Mantle for smart-money rotations and protocol-level flow anomalies, produces explainable alpha signals, and records prediction commitments on-chain.

## Target Users

- Mantle ecosystem traders looking for early capital-flow signals
- Web3 researchers tracking smart-money behavior
- DeFi communities that want Telegram or Discord alpha alerts
- Hackathon judges evaluating agentic AI with on-chain benchmarking

## Core User Story

As a Mantle user, I want an autonomous agent to detect unusual smart-money or protocol activity, explain why it may matter, and show whether its prior predictions were correct.

## MVP Scope

### Must Have

- Run an alpha scan from the dashboard or API.
- Detect at least three signal types:
  - smart-money cohort rotation
  - protocol flow spike
  - yield-asset accumulation
- Produce a structured signal with:
  - asset or protocol
  - direction
  - confidence
  - time horizon
  - evidence
  - natural-language thesis
  - prediction metric
- Generate a deterministic signal hash.
- Provide a Solidity contract for recording signal commitments and outcomes.
- Show signal history in a dashboard-ready format.

### Should Have

- Telegram or Discord alert payload formatting.
- Mantle Sepolia deployment script.
- Outcome resolver for hit, miss, and pending signals.
- Public agent card or manifest describing capabilities.

### Out of Scope for MVP

- Automatic trading.
- Custody or wallet signing on behalf of users.
- Investment advice claims.
- Full-chain real-time indexing.
- Private smart-money deanonymization.

## Differentiation

This is not a wallet guard or approval scanner. The product analyzes groups of wallets, protocol flows, and market context to discover opportunities, then benchmarks the agent's predictions on-chain.

## Success Criteria

- A judge can trigger a scan and see an alpha signal in under 30 seconds.
- Every signal includes evidence and a confidence score.
- The signal hash can be recorded on Mantle Sepolia.
- The demo clearly shows agent track record and outcome benchmarking.

