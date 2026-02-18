import requests
import time
import json
from datetime import datetime

# Sources
SOURCES = [
    "https://api.dexscreener.com/token-boosts/latest/v1",
    "https://api.dexscreener.com/latest/dex/search?q=Base"
]

GOPLUS_API = "https://api.gopluslabs.io/api/v1/token_security/8453"

def check_security(address):
    """
     audits the token contract using GoPlus Security API
    """
    try:
        url = f"{GOPLUS_API}?contract_addresses={address}"
        response = requests.get(url)
        data = response.json()
        
        if data.get('code') != 1:
            return False, "Audit Failed"
            
        result = data.get('result', {}).get(address.lower(), {})
        
        # 1. Critical Security Checks
        if result.get('is_honeypot') == "1":
            return False, "HONEYPOT 🚨"
            
        if result.get('is_open_source') == "0":
            return False, "Closed Source ⚠️"
            
        if result.get('is_proxy') == "1":
            return False, "Proxy Contract ⚠️"

        # 2. Tax Checks
        buy_tax = result.get('buy_tax', '0')
        sell_tax = result.get('sell_tax', '0')
        
        # Handle cases where tax is empty string
        if buy_tax == "": buy_tax = "0"
        if sell_tax == "": sell_tax = "0"
        
        if float(buy_tax) > 10 or float(sell_tax) > 10:
            return False, f"High Tax (B:{buy_tax}% S:{sell_tax}%)"

        # 3. Liquidity/Owner Checks
        # This is tricky via API alone, but we can warn
        # If top LP holder is not locked and holds > 90%, it's a rug risk
        lp_holders = result.get('lp_holders', [])
        if lp_holders:
            top_lp = lp_holders[0]
            if float(top_lp.get('percent', 0)) > 0.90 and int(top_lp.get('is_locked', 0)) == 0:
                 return False, "Liquidity Unlocked (100% Risk)"

        return True, "Safe"

    except Exception as e:
        # If audit fails, we skip to be safe
        return False, f"Audit Error: {e}"

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
    Advanced Gem Finder Strategy - Aggregated + Security Audited
    """
    print("💎 Running 'The Validator' + 'The Auditor' Strategy...")
    print("Criteria: Liq > $8k | Vol > $10k | Socials | AUDITED (No Honeypots/Unlocked LP)")
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
        price_change_m5 = float(pair.get('priceChange', {}).get('m5', 0)) # Immediate trend
        price_change_1h = float(pair.get('priceChange', {}).get('h1', 0))
        price_change_6h = float(pair.get('priceChange', {}).get('h6', 0))
        pair_created_at = pair.get('pairCreatedAt', None)
        base_token = pair.get('baseToken', {})
        token_address = base_token.get('address')
        
        # 2. "The Validator" Logic (Strict Filters)
        
        # Liquidity & Volume Floors
        if liquidity < 8000: continue
        if volume_24h < 10000: continue
            
        # Socials Check
        info = pair.get('info', {})
        socials = info.get('socials', [])
        websites = info.get('websites', [])
        if not socials and not websites:
            continue 
            
        # 3. "Trend Scanner" (Anti-Dump & Zombie Check)
        
        # Zombie Check: High volume but 0% price movement = Suspicious (Wash trading or Honeypot)
        if volume_24h > 50000 and abs(price_change_1h) < 0.1:
             print(f"⚠️  Skipping {base_token.get('symbol')}: Zombie Price Action (High Vol, 0% Move)")
             continue

        # Falling Knife Check: Crashed in last 5 mins
        if price_change_m5 < -5:
             print(f"⚠️  Skipping {base_token.get('symbol')}: Falling Knife (-{abs(price_change_m5)}% in 5m)")
             continue
             
        # Dead Token Check: Down bad on the 6h
        if price_change_6h < -30:
             print(f"⚠️  Skipping {base_token.get('symbol')}: Dumped (-{abs(price_change_6h)}% in 6h)")
             continue

        # 4. SECURITY AUDIT (GoPlus)
        is_safe, audit_msg = check_security(token_address)
        if not is_safe:
            print(f"⚠️  Skipping {base_token.get('symbol')}: {audit_msg}")
            continue

        # 5. Scoring System
        score = 0
        if price_change_m5 > 0: score += 10 # Rising NOW
        if price_change_1h > 0: score += 20
        score += min(price_change_1h, 50) 
        
        ratio = volume_24h / liquidity
        if 0.5 < ratio < 10: score += 30
        elif ratio > 10: score += 15 # Penalize insane ratios slightly in scoring (high risk)
            
        if pair_created_at:
            age_hours = (datetime.now().timestamp() - (pair_created_at/1000)) / 3600
            if age_hours < 24: score += 40
            elif age_hours < 72: score += 20
        
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
            "address": token_address
        })

    # Sort by Score
    gems.sort(key=lambda x: x['score'], reverse=True)
    
    if not gems:
        print("No gems passed the AUDIT and filter.")
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
