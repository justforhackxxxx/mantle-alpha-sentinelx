# Deployment

## Mantle Sepolia SignalRegistry

The MVP contract is `contracts/SignalRegistry.sol`. It records alpha signal commitments before outcomes are known.

### 1. Prepare Environment

```bash
cp .env.example .env
```

Edit `.env`:

```text
MANTLE_SEPOLIA_RPC_URL=https://rpc.sepolia.mantle.xyz
DEPLOYER_PRIVATE_KEY=...
SIGNAL_REGISTRY_ADDRESS=0x0000000000000000000000000000000000000000
```

Never commit `.env` or a real private key.

### 2. Install Foundry

```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

### 3. Deploy

```bash
./scripts/deploy_signal_registry.sh
```

Copy the deployed contract address into `.env`:

```text
SIGNAL_REGISTRY_ADDRESS=0x...
```

Restart the API:

```bash
cd apps/api
python3 main.py
```

### 4. Verify Demo Commitment

```bash
curl http://127.0.0.1:8787/api/alpha/commitment-preview
```

The response should show:

- `chainId: 5003`
- `contract.address: <your deployed SignalRegistry>`
- `method: recordSignal(...)`
- `calldata` beginning with `0xb0ea9be1`

## Current Hackathon Deployment

The demo deployment used for judging is:

```text
Network: Mantle Sepolia
Chain ID: 5003
SignalRegistry: 0xB06b9AB4B9bD74Fdb45E6F0428ed0512C7B2Fb90
Signal commitment tx: 0xf7d6c4b51eb42bafdbf9b79f7f630c621750346557cc37a597c0a63863ba5c51
Signal hash: 0xb11162f187457f18423a1659d20ce689bbdb7a600c3aec3d4c082258907d0000
```

Explorer links:

- https://sepolia.mantlescan.xyz/address/0xB06b9AB4B9bD74Fdb45E6F0428ed0512C7B2Fb90
- https://sepolia.mantlescan.xyz/tx/0xf7d6c4b51eb42bafdbf9b79f7f630c621750346557cc37a597c0a63863ba5c51
