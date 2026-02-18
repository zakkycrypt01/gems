import sys
import time

def track_wallet(address):
    print(f"🕵️‍♂️ Tracking Smart Money: {address}")
    print("Listening for transactions on Base...")
    
    # Mock loop for demonstration
    # Real implementation would use web3.py websocket subscription
    try:
        while True:
            time.sleep(2)
            # Check for txs...
            pass
    except KeyboardInterrupt:
        print("\nStopping tracker.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 track_wallet.py --address <WALLET_ADDRESS>")
        sys.exit(1)
    
    wallet_address = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1] # Handle --address flag loosely
    track_wallet(wallet_address)
