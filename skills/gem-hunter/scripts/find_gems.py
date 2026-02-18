import requests
import time
import json
from datetime import datetime

# Sources
SOURCES = [
    "https://api.dexscreener.com/token-boosts/latest/v1",
    "https://api.dexscreener.com/latest/dex/search?q=Base"
]

def get_pair_data(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return []
        data = response.json()
        if isinstance(data, list): # Boosts endpoint returns a list
            # We need to fetch pair details for boosts
            pairs = []
            for item in data[:30]: # Check top 30 boosts
                if item.get('chainId') == 'base' and item.get('tokenAddress'):
                    # Fetch specific pair
                    pair_url = f"https://api.dexscreener.com/latest/dex/tokens/{item.get('tokenAddress')}"
                    p_res = requests.get(pair_url)
                    if p_res.status_code == 200:
                        p_data = p_res.json()
                        if p_data.get('pairs'):
                            # Add the most liquid pair
                            best = max(p_data['pairs'], key=lambda x: float(x.get('liquidity', {}).get('usd', 0)))
                            pairs.append(best)
            return pairs
        else:
            return data.get('pairs', [])
    except:
        return []

def get_time_ago(timestamp):
    if not timestamp:
        return "Unknown"
    created = datetime.fromtimestamp(timestamp / 1000)
    now = datetime.now()
    diff = now - created
    hours = diff.total_seconds() / 3600
    if hours < 1:
        return f"{int(diff.total_seconds() / 60)}m ago"
    return f"{hours:.1f}h ago"

def find_gems():
    """
    Advanced Gem Finder Strategy - Aggregated Sources
    """
    print("💎 Running 'The Validator' Strategy (Aggregated)...")
    print("Criteria: Liq > $8k | Vol > $10k | Has Socials | Score-based Ranking")
    print("--------------------------------------------------")
    
    all_pairs = []
    seen_addresses = set()

    # 1. Aggregate Data
    for source in SOURCES:
        pairs = get_pair_data(source)
        for pair in pairs:
            addr = pair.get('pairAddress')
            if addr not in seen_addresses and pair.get('chainId') == 'base':
                all_pairs.append(pair)
                seen_addresses.add(addr)

    print(f"Scanned {len(all_pairs)} unique pairs on Base.")
    
    gems = []
    
    for pair in all_pairs:
        # Metrics
        liquidity = float(pair.get('liquidity', {}).get('usd', 0))
        volume_24h = float(pair.get('volume', {}).get('h24', 0))
        price_change_1h = float(pair.get('priceChange', {}).get('h1', 0))
        price_change_6h = float(pair.get('priceChange', {}).get('h6', 0))
        pair_created_at = pair.get('pairCreatedAt', None)
        
        # 2. Relaxed "Validator" Logic
        
        # Liquidity Floor (Lowered to $8k to catch earlier ones)
        if liquidity < 8000: 
            continue
            
        # Volume Floor (Lowered to $10k)
        if volume_24h < 10000:
            continue
            
        # Socials Check (Still Mandatory - otherwise it's a ghost chain)
        info = pair.get('info', {})
        socials = info.get('socials', [])
        websites = info.get('websites', [])
        if not socials and not websites:
            continue 
            
        # 3. Scoring System
        score = 0
        
        # Momentum
        if price_change_1h > 0: score += 20
        if price_change_6h > 0: score += 10
        score += min(price_change_1h, 50) # Cap momentum bonus
        
        # Volume/Liq Ratio (Velocity)
        ratio = volume_24h / liquidity
        if 0.5 < ratio < 10: # Healthy trading range
            score += 30
        elif ratio > 10: # Insane velocity (could be botting, but also could be mooning)
            score += 15
            
        # Freshness Bonus
        if pair_created_at:
            age_hours = (datetime.now().timestamp() - (pair_created_at/1000)) / 3600
            if age_hours < 24: score += 40
            elif age_hours < 72: score += 20
        
        base_token = pair.get('baseToken', {})
        
        gems.append({
            "symbol": base_token.get('symbol'),
            "name": base_token.get('name'),
            "price": pair.get('priceUsd'),
            "liquidity": liquidity,
            "volume": volume_24h,
            "change_1h": price_change_1h,
            "age": get_time_ago(pair_created_at),
            "url": pair.get('url'),
            "score": score,
            "address": base_token.get('address')
        })

    # Sort by Score
    gems.sort(key=lambda x: x['score'], reverse=True)
    
    if not gems:
        print("No gems found even with relaxed filters.")
        return

    for gem in gems[:10]:
        print(f"🌟 {gem['name']} ({gem['symbol']}) | Score: {int(gem['score'])}")
        print(f"   💰 Price: ${gem['price']} | 1h: {gem['change_1h']}%")
        print(f"   💧 Liq: ${gem['liquidity']:,.0f} | 📊 Vol: ${gem['volume']:,.0f}")
        print(f"   ⏳ Age: {gem['age']}")
        print(f"   🔗 {gem['url']}")
        print(f"   📋 {gem['address']}")
        print("--------------------------------------------------")

if __name__ == "__main__":
    find_gems()
