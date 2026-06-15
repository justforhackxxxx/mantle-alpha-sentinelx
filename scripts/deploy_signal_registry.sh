#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v forge >/dev/null 2>&1; then
  echo "forge is required. Install Foundry first: https://book.getfoundry.sh/getting-started/installation" >&2
  exit 1
fi

if [[ -f ".env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source ".env"
  set +a
fi

: "${MANTLE_SEPOLIA_RPC_URL:?Set MANTLE_SEPOLIA_RPC_URL in .env}"
: "${DEPLOYER_PRIVATE_KEY:?Set DEPLOYER_PRIVATE_KEY in .env}"

forge create \
  --rpc-url "$MANTLE_SEPOLIA_RPC_URL" \
  --private-key "$DEPLOYER_PRIVATE_KEY" \
  contracts/SignalRegistry.sol:SignalRegistry

