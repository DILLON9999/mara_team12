import requests
from datetime import datetime, timedelta
from gridstatusio import GridStatusClient
import pandas as pd
from gridstatus import Ercot, SPP, NYISO, ISONE, IESO

MINER_WTH = 100

# Dollar per megawatt-hour
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

def calculate_hourly_mining_profit(lmp_per_mwh, hashprice_per_th_day, miner_efficiency_watts_per_th=MINER_WTH):
    """
    Calculate hourly profitability of BTC mining given LMP electricity costs
    
    Args:
        lmp_per_mwh: Electricity price in $/MWh
        hashprice_per_th_day: BTC mining revenue in $/TH/day  
        miner_efficiency_watts_per_th: Power consumption in watts per TH/s (default: 100W/TH but can change)
    
    Returns:
        dict with hourly profit/loss per TH
    """
    # Convert LMP from $/MWh to $/kWh
    lmp_per_kwh = lmp_per_mwh / 1000
    
    # Convert hashprice from daily to hourly
    hashprice_per_th_hour = hashprice_per_th_day / 24
    
    # Calculate hourly electricity cost per TH
    # miner_efficiency_watts_per_th / 1000 = kW per TH
    electricity_cost_per_th_hour = (miner_efficiency_watts_per_th / 1000) * lmp_per_kwh
    
    # Calculate net hourly profit per TH
    hourly_profit_per_th = hashprice_per_th_hour - electricity_cost_per_th_hour
    
    return {
        'hourly_revenue_per_th': round(hashprice_per_th_hour, 4),
        'hourly_electricity_cost_per_th': round(electricity_cost_per_th_hour, 4),
        'hourly_profit_per_th': round(hourly_profit_per_th, 4),
        'lmp_per_kwh': round(lmp_per_kwh, 4),
        'miner_watts_per_th': miner_efficiency_watts_per_th
    }

# Carbon emissions factors in gCO2/MWh
CARBON_FACTORS = {
    "coal": 1001,
    "natural gas": 469,
    "oil": 840,
    "nuclear": 0,
    "wind": 0,
    "solar": 0,
    "hydro": 0,
    "battery": 0,
    "other": 300,
}

def get_carbon_intensity_by_iso():
    """Fetch current carbon intensity for each ISO"""
    print("Fetching carbon intensity data from ISOs...")
    
    isos = {
        "ercot": Ercot(),
        "spp": SPP(),
        "nyiso": NYISO(),
        "isone": ISONE(),
        "ieso": IESO()
    }
    
    carbon_intensities = {}
    
    for region_key, iso in isos.items():
        try:
            # Get today's fuel mix
            today = datetime.now().date()
            df = iso.get_fuel_mix(date=today)
            
            if df is not None and not df.empty:
                # Get the most recent data
                latest_row = df.iloc[-1]
                
                # Calculate total generation and emissions
                total_gen = 0
                total_emissions = 0
                
                for col in df.columns:
                    if col not in ['Time', 'time', 'datetime', 'interval_start', 'interval_end']:
                        fuel_type = col.lower()
                        value = float(latest_row[col]) if pd.notna(latest_row[col]) else 0
                        
                        # Map fuel type to carbon factor
                        emission_factor = CARBON_FACTORS.get(fuel_type, 300)
                        
                        total_gen += value
                        total_emissions += emission_factor * value
                
                # Calculate carbon intensity (gCO2/MWh)
                carbon_intensity = round(total_emissions / total_gen, 2) if total_gen > 0 else 0
                carbon_intensities[region_key] = carbon_intensity
                print(f"  {region_key.upper()}: {carbon_intensity} gCO2/MWh")
            else:
                carbon_intensities[region_key] = None
                print(f"  {region_key.upper()}: No data available")
                
        except Exception as e:
            print(f"  Error fetching {region_key}: {str(e)}")
            carbon_intensities[region_key] = None
    
    # Add estimates for CAISO, MISO, PJM (not available via gridstatus)
    carbon_intensities['caiso'] = 250  # California typically cleaner
    carbon_intensities['miso'] = 600   # Mixed coal/gas
    carbon_intensities['pjm'] = 550    # Mixed coal/gas/nuclear
    
    return carbon_intensities

def calculate_profit_per_carbon_intensity(lmp_data, btc_hashprice, carbon_intensities):
    """Calculate profit per carbon intensity for each ISO region"""
    results = []
    
    for iso_name, iso_data in lmp_data.items():
        if 'error' not in iso_data and 'average_lmp' in iso_data:
            # Calculate mining profitability
            profit = calculate_hourly_mining_profit(
                iso_data['average_lmp'], 
                btc_hashprice['hashprice_per_th_day']
            )
            
            # Get carbon intensity
            carbon_intensity = carbon_intensities.get(iso_name)
            
            if carbon_intensity and carbon_intensity > 0:
                # Profit per unit of carbon ($/gCO2)
                profit_per_carbon = profit['hourly_profit_per_th'] / carbon_intensity * 1000
                
                results.append({
                    'iso': iso_name.upper(),
                    'avg_lmp': iso_data['average_lmp'],
                    'hourly_profit_per_th': profit['hourly_profit_per_th'],
                    'carbon_intensity': carbon_intensity,
                    'profit_per_carbon': profit_per_carbon,
                    'profitable': profit['hourly_profit_per_th'] > 0
                })
    
    # Sort by profit per carbon (descending)
    results.sort(key=lambda x: x['profit_per_carbon'], reverse=True)
    
    return results

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
    
    # Get carbon intensity data
    print("\n=== CARBON INTENSITY BY ISO ===")
    carbon_intensities = get_carbon_intensity_by_iso()
    
    # Calculate profit per carbon intensity for all regions
    print("\n=== MINING PROFIT PER CARBON INTENSITY ===")
    profit_carbon_results = calculate_profit_per_carbon_intensity(lmp_data, btc, carbon_intensities)
    
    print("\nRegion Rankings (Best Profit/Carbon Ratio):")
    print("-" * 80)
    print(f"{'ISO':<8} {'Avg LMP':<12} {'Profit/TH/hr':<15} {'Carbon':<12} {'Profit/Carbon':<15}")
    print(f"{'':8} {'($/MWh)':<12} {'($)':<15} {'(gCO2/MWh)':<12} {'($/kgCO2)':<15}")
    print("-" * 80)
    
    for result in profit_carbon_results:
        print(f"{result['iso']:<8} "
              f"${result['avg_lmp']:>10.2f} "
              f"${result['hourly_profit_per_th']:>13.4f} "
              f"{result['carbon_intensity']:>11.0f} "
              f"${result['profit_per_carbon']:>13.4f}")
    
    print("-" * 80)
    print("\nKey Insights:")
    best = profit_carbon_results[0] if profit_carbon_results else None
    if best:
        print(f"• Best profit/carbon ratio: {best['iso']} at ${best['profit_per_carbon']:.4f}/kgCO2")
        print(f"• This means: For every kg of CO2 emitted, you earn ${best['profit_per_carbon']:.4f}")
        
    # Show unprofitable regions
    unprofitable = [r for r in profit_carbon_results if not r['profitable']]
    if unprofitable:
        print(f"\n• Unprofitable regions: {', '.join([r['iso'] for r in unprofitable])}") 