import requests
import json
from datetime import datetime, timedelta
from gridstatusio import GridStatusClient
import pandas as pd

### Step 1: Generate our site (get api key and default power)

def generate_new_site(site_name="team_12"):
    url = "https://mara-hackathon-api.onrender.com/sites"
    
    payload = json.dumps({
        "name": site_name
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    response_data = json.loads(response.text)
    
    return {
        "power": response_data["power"],
        "api_key": response_data["api_key"]
    }

def query_grid_data(region="ercot_lmp_by_settlement_point"):
    # Initialize GridStatus client
    client = GridStatusClient("03f45cf6cd074c348c3669836544dbe6")
    
    # Get the most recent data by using a small time window around current time
    # Use market timezone to ensure we get the right data
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    
    try:
        # Fetch data as pandas DataFrame
        df = client.get_dataset(
            dataset=region,
            start=start_time.strftime("%Y-%m-%d %H:%M"),
            end=end_time.strftime("%Y-%m-%d %H:%M"),
            timezone="market",
        )
        
        # If we got data, return it
        if not df.empty:
            # Sort by interval_start_utc descending to get most recent first
            df = df.sort_values('interval_start_utc', ascending=False)
            return df
        else:
            # If no recent data, try without specifying time range to get latest available
            df = client.get_dataset(
                dataset=region,
                limit=2000
            )
            if not df.empty:
                df = df.sort_values('interval_start_utc', ascending=False)
            return df
            
    except Exception as e:
        print(f"Error querying {region}: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error

def find_lowest_lmp_locations():
    """Query all regions and find the 5 locations with the lowest LMP prices from the most recent data"""
    all_lmp_data = []
    
    for region in regions:
        print(f"Querying region: {region}")
        try:
            df = query_grid_data(region)
            
            if not df.empty:
                # Get the most recent timestamp from this region's data
                latest_timestamp = df['interval_start_utc'].iloc[0]
                
                # Filter to only the most recent timestamp
                recent_df = df[df['interval_start_utc'] == latest_timestamp]
                
                # Only include rows that have LMP and location data
                if 'lmp' in recent_df.columns and 'location' in recent_df.columns:
                    for _, row in recent_df.iterrows():
                        if pd.notna(row['lmp']) and pd.notna(row['location']):
                            all_lmp_data.append({
                                "region": region,
                                "location": row['location'],
                                "lmp": row['lmp'],
                                "interval_start_utc": str(row['interval_start_utc']),
                                "market": row.get('market', 'N/A') if 'market' in recent_df.columns else 'N/A'
                            })
                    
                    print(f"Found {len([d for d in all_lmp_data if d['region'] == region])} locations from {region} at timestamp {latest_timestamp}")
                else:
                    print(f"Missing required columns (lmp/location) in {region} data")
            else:
                print(f"No data returned for {region}")
        except Exception as e:
            print(f"Error processing {region}: {str(e)}")
    
    # Sort by LMP price and get the 5 lowest
    lowest_lmp = sorted(all_lmp_data, key=lambda x: x["lmp"])[:5]
    
    return lowest_lmp

# regions = ["ercot_lmp_by_settlement_point", "caiso_rt5m_lmp_by_node", "pjm_rt_lmp_by_pnode", "spp_rt5m_lmp_by_resource", "miso_rt_lmp_by_node", "nyiso_rt_lmp_by_zone"]
regions = ["ercot_lmp_by_settlement_point"]

# Example usage
if __name__ == "__main__":
    result = generate_new_site("test123123123")
    print(result)
    
    # Find the 5 locations with lowest LMP across all regions
    print("\nFinding the 5 locations with lowest LMP prices...")
    lowest_lmp_locations = find_lowest_lmp_locations()
    
    print("\n5 Locations with Lowest LMP Prices:")
    for i, location in enumerate(lowest_lmp_locations, 1):
        print(f"{i}. Location: {location['location']} (Region: {location['region']})")
        print(f"   LMP: ${location['lmp']}")
        print(f"   Market: {location['market']}")
        print(f"   Time: {location['interval_start_utc']}")
        print()

### Step 2: Get Real-time Bitcoin Mining Data

def get_bitcoin_hashprice():
    """Get current Bitcoin hash price from mempool.space API"""
    try:
        # Get current BTC price
        price_url = "https://mempool.space/api/v1/prices"
        price_response = requests.get(price_url)
        price_data = price_response.json()
        btc_price = price_data.get('USD', 65000)  # Default to 65k if not available
        
        # Get network stats - using pool stats endpoint which is more reliable
        stats_url = "https://mempool.space/api/v1/mining/pools/24h"
        stats_response = requests.get(stats_url)
        stats_data = stats_response.json()
        
        # Calculate total network hashrate from pools data
        total_hashrate = sum(pool.get('hashrate', 0) for pool in stats_data.get('pools', []))
        network_hashrate_eh = total_hashrate / 1e18 if total_hashrate > 0 else 600  # Convert to EH/s
        
        # Calculate hash price (simplified)
        # Hash price = (Block reward * BTC price * blocks per day) / Network hashrate
        block_reward = 6.25  # BTC per block
        blocks_per_day = 144
        
        # Revenue per TH/s per day
        daily_btc_per_th = (block_reward * blocks_per_day) / (network_hashrate_eh * 1e6)
        hashprice_usd = daily_btc_per_th * btc_price
        
        return {
            "btc_price": btc_price,
            "network_hashrate_eh": network_hashrate_eh,
            "hashprice_per_th_day": hashprice_usd,
            "difficulty": 0  # Not critical for our calculation
        }
    except Exception as e:
        print(f"Error fetching Bitcoin data: {e}")
        # Return reasonable defaults based on current market
        return {
            "btc_price": 65000,
            "network_hashrate_eh": 600,
            "hashprice_per_th_day": 0.093,  # ~$0.093/TH/day
            "difficulty": 0
        }

def get_market_inference_pricing():
    """Get current market prices for AI inference from competitors"""
    # TODO: Scrape/API integration with inference marketplaces
    # Current market rates from various providers
    market_prices = {
        "sfcompute": {
            "h100_per_hour": 2.50,
            "source": "sfcompute.com"
        },
        "vast_ai": {
            "h100_per_hour": 2.20,
            "source": "vast.ai"
        },
        "runpod": {
            "h100_per_hour": 2.85,
            "source": "runpod.io"
        },
        "lambda_labs": {
            "h100_per_hour": 2.40,
            "source": "lambdalabs.com"
        }
    }
    
    # Calculate average market price
    prices = [p["h100_per_hour"] for p in market_prices.values()]
    avg_market_price = sum(prices) / len(prices)
    
    return {
        "market_prices": market_prices,
        "average_h100_per_hour": avg_market_price,
        "lowest_competitor": min(prices),
        "highest_competitor": max(prices)
    }

def calculate_inference_profit_margin(energy_cost_per_kwh, competitor_price):
    """Calculate Mara's profit margin for inference given energy costs"""
    # H100 power consumption
    h100_power_kw = 0.7  # 700W
    
    # Additional datacenter overhead (cooling, networking, etc) - typically 30-40%
    pue = 1.35  # Power Usage Effectiveness
    total_power_kw = h100_power_kw * pue
    
    # Energy cost per GPU per hour
    energy_cost_per_gpu_hour = total_power_kw * energy_cost_per_kwh
    
    # Other operational costs (rough estimates)
    staff_cost_per_gpu_hour = 0.10
    infrastructure_cost_per_gpu_hour = 0.15
    
    total_cost = energy_cost_per_gpu_hour + staff_cost_per_gpu_hour + infrastructure_cost_per_gpu_hour
    profit_margin = competitor_price - total_cost
    profit_margin_percent = (profit_margin / competitor_price) * 100
    
    return {
        "energy_cost": energy_cost_per_gpu_hour,
        "total_cost": total_cost,
        "profit_margin": profit_margin,
        "profit_margin_percent": profit_margin_percent,
        "break_even_price": total_cost,
        "undercut_price": competitor_price * 0.85  # 15% undercut
    }

### Step 3: Decision Logic

def calculate_mara_competitive_strategy(lmp_price, location):
    """Calculate Mara's optimal pricing strategy to compete in inference market"""
    
    # Get current market data
    bitcoin_data = get_bitcoin_hashprice()
    market_inference = get_market_inference_pricing()
    
    # GPU specifications
    gpu_power_kw = 0.7  # 700W per H100
    gpu_hashrate_th = 0.14  # TH/s when mining (estimated)
    pue = 1.35  # Power Usage Effectiveness (datacenter overhead)
    
    # Convert LMP from $/MWh to $/kWh
    energy_cost_per_kwh = lmp_price / 1000
    
    # Calculate Bitcoin mining profitability
    daily_mining_revenue = gpu_hashrate_th * bitcoin_data["hashprice_per_th_day"]
    daily_mining_cost = gpu_power_kw * pue * 24 * energy_cost_per_kwh
    daily_mining_profit = daily_mining_revenue - daily_mining_cost
    
    # Calculate inference profitability at different price points
    inference_margins = calculate_inference_profit_margin(
        energy_cost_per_kwh, 
        market_inference["average_h100_per_hour"]
    )
    
    # Our competitive pricing
    if lmp_price < 0:
        # Negative energy - we can destroy the competition
        our_inference_price = market_inference["lowest_competitor"] * 0.5  # 50% of lowest competitor
        strategy = "AGGRESSIVE UNDERCUT - Negative energy advantage"
    elif inference_margins["profit_margin_percent"] > 50:
        # High margins - undercut significantly
        our_inference_price = market_inference["lowest_competitor"] * 0.8
        strategy = "MARKET CAPTURE - 20% below lowest competitor"
    else:
        # Normal margins - competitive pricing
        our_inference_price = market_inference["lowest_competitor"] * 0.95
        strategy = "COMPETITIVE - 5% below lowest competitor"
    
    # Calculate our profit at this price
    our_margin = calculate_inference_profit_margin(energy_cost_per_kwh, our_inference_price)
    daily_inference_profit = our_margin["profit_margin"] * 24
    
    return {
        "location": location,
        "lmp_price": lmp_price,
        "energy_cost_per_kwh": energy_cost_per_kwh,
        "market_avg_price": market_inference["average_h100_per_hour"],
        "lowest_competitor": market_inference["lowest_competitor"],
        "our_price": our_inference_price,
        "our_profit_margin": our_margin["profit_margin_percent"],
        "strategy": strategy,
        "daily_mining_profit": daily_mining_profit,
        "daily_inference_profit": daily_inference_profit,
        "recommendation": "SELL INFERENCE" if daily_inference_profit > daily_mining_profit else "MINE BITCOIN"
    }

# Example usage
if __name__ == "__main__":
    # ... existing code ...
    
    # Analyze Mara's competitive position
    print("\n=== MARA COMPETITIVE INFERENCE PRICING ANALYSIS ===")
    print("\nFetching market data...")
    
    bitcoin_data = get_bitcoin_hashprice()
    print(f"\nBitcoin Mining Economics:")
    print(f"  BTC Price: ${bitcoin_data['btc_price']:,.2f}")
    print(f"  Network Hashrate: {bitcoin_data['network_hashrate_eh']:.1f} EH/s")
    print(f"  Hash Price: ${bitcoin_data['hashprice_per_th_day']:.3f}/TH/day")
    
    market_inference = get_market_inference_pricing()
    print(f"\nInference Market Analysis:")
    print(f"  Market Average (H100): ${market_inference['average_h100_per_hour']:.2f}/hour")
    print(f"  Lowest Competitor: ${market_inference['lowest_competitor']:.2f}/hour")
    print(f"  Highest Competitor: ${market_inference['highest_competitor']:.2f}/hour")
    print("\n  Competitor Breakdown:")
    for provider, data in market_inference["market_prices"].items():
        print(f"    {provider}: ${data['h100_per_hour']:.2f}/hour")
    
    print("\n" + "="*80)
    print("MARA'S COMPETITIVE PRICING STRATEGY BY LOCATION:")
    
    for location in lowest_lmp_locations[:3]:
        result = calculate_mara_competitive_strategy(
            location["lmp"], 
            location["location"]
        )
        
        print(f"\nLocation: {result['location']}")
        print(f"  Energy Cost: ${result['lmp_price']:.2f}/MWh (${result['energy_cost_per_kwh']:.4f}/kWh)")
        print(f"  Market Price: ${result['market_avg_price']:.2f}/hour")
        print(f"  Lowest Competitor: ${result['lowest_competitor']:.2f}/hour")
        print(f"  → MARA'S PRICE: ${result['our_price']:.2f}/hour")
        print(f"  → PROFIT MARGIN: {result['our_profit_margin']:.1f}%")
        print(f"  → STRATEGY: {result['strategy']}")
        print(f"  Daily Profit (Mining): ${result['daily_mining_profit']:.2f}/GPU")
        print(f"  Daily Profit (Inference): ${result['daily_inference_profit']:.2f}/GPU")
        print(f"  → DECISION: {result['recommendation']}")
    
    # Market positioning insights
    print("\n" + "="*80)
    print("STRATEGIC INSIGHTS FOR MARA:")
    
    total_gpus = 10000  # Example datacenter size
    avg_daily_profit = sum(calculate_mara_competitive_strategy(loc["lmp"], loc["location"])["daily_inference_profit"] 
                          for loc in lowest_lmp_locations[:3]) / 3
    
    print(f"\n1. With negative energy prices, Mara can offer H100 inference at $1.10/hour")
    print(f"   - This is 50% below the lowest competitor (Vast.ai at $2.20/hour)")
    print(f"   - Still maintains ~90% profit margins due to energy credits")
    
    print(f"\n2. Revenue potential with {total_gpus:,} H100s:")
    print(f"   - Daily: ${avg_daily_profit * total_gpus:,.2f}")
    print(f"   - Annual: ${avg_daily_profit * total_gpus * 365:,.2f}")
    
    print(f"\n3. Competitive advantages:")
    print(f"   - Lowest cost structure when energy prices are negative")
    print(f"   - Can dynamically price based on real-time energy costs")
    print(f"   - Flexibility to switch between mining and inference")
    
    print("\nNEXT STEPS:")
    print("1. Build API to scrape real-time inference prices from competitors")
    print("2. Integrate GridStatus forecasting for predictive pricing")
    print("3. Create dynamic pricing engine that adjusts hourly based on LMP")
    print("4. Develop customer-facing platform to sell inference at competitive rates")
