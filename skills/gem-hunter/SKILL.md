---
name: gem-hunter
description: Track smart money, find early gems on Base, and execute trades ("ape in"). Use when the user wants to scan for new tokens, monitor wallet activity, or buy a specific token on Base.
---

# Gem Hunter

This skill provides tools to hunt for alpha on the Base chain.

## Capabilities

1.  **Scan for Gems**: continuously monitor DEXs for new liquidity pools.
2.  **Track Smart Money**: watch specific wallets for buy/sell activity.
3.  **Ape In**: execute buy orders for a token.

## Usage

### 1. Scan for Boosted Gems (Hot)

Run the scanner to find the latest boosted tokens on Base.

```bash
skills/gem-hunter/.venv/bin/python skills/gem-hunter/scripts/scan_pairs.py
```

### 2. Track Smart Money

Monitor a specific wallet address for token purchases.

```bash
skills/gem-hunter/.venv/bin/python skills/gem-hunter/scripts/track_wallet.py --address <WALLET_ADDRESS>
```

### 3. Ape In (Execute Trade)

Buy a specific token. **Requires private key in environment variables.**

```bash
skills/gem-hunter/.venv/bin/python skills/gem-hunter/scripts/buy_token.py --token <TOKEN_ADDRESS> --amount <ETH_AMOUNT>
```

## Configuration

Set the following environment variables (create a `.env` in `skills/gem-hunter/` or export them):
- `BASE_RPC_URL`: RPC endpoint for Base (default: public RPC).
- `PRIVATE_KEY`: (Optional) Your wallet private key for trading.
- `ETHERSCAN_API_KEY`: (Optional) For ABI fetching.
