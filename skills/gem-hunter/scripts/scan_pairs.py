import requests
import time
import json

# DexScreener API
# "https://api.dexscreener.com/token-boosts/latest/v1" gives boosted tokens
DEXSCREENER_BOOSTS = "https://api.dexscreener.com/token-boosts/latest/v1"

def scan_new_pairs():
    """
    Scans for boosted (hot) pairs on Base using DexScreener.
    """
    print("💎 Scanning for boosted gems on Base...")
    
    try:
        # Boosted tokens endpoint
        response = requests.get(DEXSCREENER_BOOSTS)
        response.raise_for_status()
        data = response.json()
        
        # data is a list of boosted profiles
        if not data:
            print("No boosted profiles found.")
            return

        print(f"Checking {len(data)} boosted profiles for Base chain...")
        
        found_count = 0
        for profile in data:
            chain_id = profile.get('chainId')
            if chain_id != 'base':
                continue
            
            # Boosted profiles return a token address, not full pair stats usually
            # But let's see what we get. The profile usually has links.
            # Actually, let's fetch the pair data for the token address to get stats.
            token_address = profile.get('tokenAddress')
            if not token_address:
                continue

            # Fetch pair stats for this token
            pair_url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
            pair_resp = requests.get(pair_url)
            if pair_resp.status_code != 200:
                continue
            
            pair_data = pair_resp.json()
            pairs = pair_data.get('pairs', [])
            if not pairs:
                continue
            
            # Take the most liquid pair
            best_pair = max(pairs, key=lambda p: float(p.get('liquidity', {}).get('usd', 0)))
            
            base_token = best_pair.get('baseToken', {})
            liquidity = float(best_pair.get('liquidity', {}).get('usd', 0))
            volume_24h = float(best_pair.get('volume', {}).get('h24', 0))
            pair_address = best_pair.get('pairAddress')
            url = best_pair.get('url')
            
            print(f"--------------------------------------------------")
            print(f"🔥  BOOSTED: {base_token.get('name')} ({base_token.get('symbol')})")
            print(f"💧  Liquidity: ${liquidity:,.2f}")
            print(f"📊  24h Vol:   ${volume_24h:,.2f}")
            print(f"📍  Addr:      {token_address}")
            print(f"🔗  Link:      {url}")
            print(f"--------------------------------------------------")
            
            found_count += 1
            if found_count >= 5: # Limit to top 5 for brevity
                break

        if found_count == 0:
            print("No boosted gems found on Base right now.")

    except Exception as e:
        print(f"❌ Error scanning DexScreener: {e}")

if __name__ == "__main__":
    scan_new_pairs()
