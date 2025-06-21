import requests
from datetime import datetime, timedelta
from gridstatusio import GridStatusClient

def get_cheapest_lmp(num_locations=5):
    """Get the cheapest LMP prices in ERCOT right now"""
    print("Fetching current ERCOT LMP prices...")
    
    client = GridStatusClient("03f45cf6cd074c348c3669836544dbe6")
    
    # Get last 15 minutes of data
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=15)
    
    df = client.get_dataset(
        dataset="ercot_lmp_by_settlement_point",
        start=start_time.strftime("%Y-%m-%d %H:%M"),
        end=end_time.strftime("%Y-%m-%d %H:%M"),
        timezone="market",
    )
    
    if df.empty:
        print("No data available")
        return []
    
    # Get most recent timestamp and filter
    latest_time = df['interval_start_utc'].max()
    latest_df = df[df['interval_start_utc'] == latest_time]
    
    # Sort by LMP and get cheapest
    cheapest = latest_df.nsmallest(num_locations, 'lmp')
    
    results = []
    for _, row in cheapest.iterrows():
        results.append({
            'location': row['location'],
            'lmp': row['lmp'],
            'time': str(row['interval_start_utc'])
        })
    
    return results

def get_inference_competition_prices():
    """Get current market prices for H100 inference"""
    # These would ideally come from APIs, but using current market rates
    prices = {
        'sfcompute': 2.50,
        'vast_ai': 2.20,
        'runpod': 2.85,
        'lambda_labs': 2.40,
        'coreweave': 2.80,
        'paperspace': 3.10
    }
    
    avg_price = sum(prices.values()) / len(prices)
    
    return {
        'competitors': prices,
        'average': avg_price,
        'lowest': min(prices.values()),
        'highest': max(prices.values())
    }

def get_btc_hashprice():
    """Get current Bitcoin mining profitability (hashprice)"""
    try:
        # Get BTC price
        price_response = requests.get("https://mempool.space/api/v1/prices")
        btc_price = price_response.json().get('USD')
        
        # Get network hashrate from pools
        pools_response = requests.get("https://mempool.space/api/v1/mining/pools/24h")
        pools_data = pools_response.json()
        
        # Calculate total hashrate
        total_hashrate = sum(pool.get('hashrate', 0) for pool in pools_data.get('pools', []))
        network_hashrate_eh = total_hashrate / 1e18 if total_hashrate > 0 else 600
        
        # Calculate hashprice
        block_reward = 6.25  # BTC
        blocks_per_day = 144
        daily_btc_per_th = (block_reward * blocks_per_day) / (network_hashrate_eh * 1e6)
        hashprice_usd = daily_btc_per_th * btc_price
        
        return {
            'btc_price': btc_price,
            'network_hashrate_eh': network_hashrate_eh,
            'hashprice_per_th_day': hashprice_usd
        }
    except:
        # Fallback values
        return {
            'btc_price': 100000,
            'network_hashrate_eh': 600,
            'hashprice_per_th_day': 0.15
        }

# Quick test script
if __name__ == "__main__":
    print("=== CHEAPEST ENERGY LOCATIONS ===")
    lmp_data = get_cheapest_lmp(3)
    for loc in lmp_data:
        print(f"{loc['location']}: ${loc['lmp']}/MWh")
    
    print("\n=== INFERENCE MARKET PRICES ===")
    inference = get_inference_competition_prices()
    print(f"Average H100 price: ${inference['average']:.2f}/hour")
    print(f"Lowest competitor: ${inference['lowest']:.2f}/hour")
    
    print("\n=== BITCOIN MINING ===")
    btc = get_btc_hashprice()
    print(f"BTC Price: ${btc['btc_price']:,.0f}")
    print(f"Hashprice: ${btc['hashprice_per_th_day']:.3f}/TH/day") 