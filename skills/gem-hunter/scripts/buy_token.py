import sys
import os

def buy_token(token_address, amount):
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        print("❌ Error: PRIVATE_KEY not found in environment variables.")
        return

    print(f"🦍 APE IN initiated!")
    print(f"Token: {token_address}")
    print(f"Amount: {amount} ETH")
    
    # Real implementation would construct and sign a tx via web3.py
    # interacting with Uniswap/Aerodrome Router
    print("...Constructing transaction...")
    print("...Signing transaction...")
    print("✅ Transaction sent: 0x123...abc (MOCK)")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python3 buy_token.py --token <TOKEN_ADDRESS> --amount <ETH_AMOUNT>")
        sys.exit(1)
        
    token = sys.argv[2]
    amount = sys.argv[4]
    buy_token(token, amount)
