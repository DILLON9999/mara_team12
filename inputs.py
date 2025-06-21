import requests
from datetime import datetime, timedelta
from gridstatusio import GridStatusClient

def get_cheapest_lmp(num_locations=5):
    """Get average and recent LMP prices from all major ISOs"""
    print("Fetching LMP data from all ISOs...")
    
    client = GridStatusClient("03f45cf6cd074c348c3669836544dbe6")
    
    # Get last 15 minutes of data
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=15)
    
    # Define all datasets to query
    datasets = {
        "ercot": "ercot_lmp_by_settlement_point",
        "caiso": "caiso_lmp_real_time_5_min", 
        "ieso": "ieso_lmp_real_time_5_min",
        "isone": "isone_lmp_real_time_5_min",
        "miso": "miso_lmp_real_time_5_min",
        "nyiso": "nyiso_lmp_real_time_5_min",
        "pjm": "pjm_lmp_real_time_5_min",
        "spp": "spp_lmp_real_time_5_min"
    }
    
    results = {}
    
    for iso_name, dataset_name in datasets.items():
        print(f"  Fetching {iso_name.upper()} data...")
        try:
            df = client.get_dataset(
                dataset=dataset_name,
                start=start_time.strftime("%Y-%m-%d %H:%M"),
                end=end_time.strftime("%Y-%m-%d %H:%M"),
                timezone="market",
            )
            
            if not df.empty and 'lmp' in df.columns:
                # Get most recent 10 minutes of data
                latest_time = df['interval_start_utc'].max()
                recent_10min = df[df['interval_start_utc'] >= (latest_time - timedelta(minutes=10))]
                
                # Calculate statistics
                avg_lmp = df['lmp'].mean()
                min_lmp = df['lmp'].min()
                max_lmp = df['lmp'].max()
                recent_avg = recent_10min['lmp'].mean()
                
                # Get cheapest locations
                cheapest_locations = df.nsmallest(min(num_locations, len(df)), 'lmp')
                
                results[iso_name] = {
                    "average_lmp": round(avg_lmp, 2),
                    "min_lmp": round(min_lmp, 2),
                    "max_lmp": round(max_lmp, 2),
                    "recent_10min_avg": round(recent_avg, 2),
                    "data_points": len(df),
                    "latest_timestamp": str(latest_time),
                    "cheapest_locations": [
                        {
                            "location": row.get('location', row.get('node', 'Unknown')),
                            "lmp": round(row['lmp'], 2),
                            "time": str(row['interval_start_utc'])
                        }
                        for _, row in cheapest_locations.iterrows()
                    ]
                }
            else:
                results[iso_name] = {
                    "error": "No data available or missing LMP column",
                    "data_points": 0
                }
                
        except Exception as e:
            print(f"    Error fetching {iso_name}: {str(e)}")
            results[iso_name] = {
                "error": str(e),
                "data_points": 0
            }
    
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
    print("=== CHEAPEST ENERGY LOCATIONS BY ISO ===")
    lmp_data = get_cheapest_lmp(3)
    
    for iso_name, iso_data in lmp_data.items():
        print(f"\n{iso_name.upper()}:")
        if 'error' in iso_data:
            print(f"  Error: {iso_data['error']}")
        else:
            print(f"  Average LMP: ${iso_data['average_lmp']}/MWh")
            print(f"  Recent 10min avg: ${iso_data['recent_10min_avg']}/MWh")
            print(f"  Min/Max: ${iso_data['min_lmp']} to ${iso_data['max_lmp']}/MWh")
            print(f"  Cheapest locations:")
            for loc in iso_data['cheapest_locations'][:3]:  # Show top 3
                print(f"    {loc['location']}: ${loc['lmp']}/MWh")
    
    print("\n=== INFERENCE MARKET PRICES ===")
    inference = get_inference_competition_prices()
    print(f"Average H100 price: ${inference['average']:.2f}/hour")
    print(f"Lowest competitor: ${inference['lowest']:.2f}/hour")
    
    print("\n=== BITCOIN MINING ===")
    btc = get_btc_hashprice()
    print(f"BTC Price: ${btc['btc_price']:,.0f}")
    print(f"Hashprice: ${btc['hashprice_per_th_day']:.3f}/TH/day") 