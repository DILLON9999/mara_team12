#!/usr/bin/env python3
"""
Demo data generator for the MARA Mining Optimization Dashboard
Provides realistic sample data for hackathon demonstrations
"""
import random
import json
from datetime import datetime, timedelta

def generate_demo_lmp_data():
    """Generate realistic demo LMP data"""
    isos = ['ercot', 'caiso', 'pjm', 'miso', 'nyiso', 'isone', 'spp']
    lmp_data = {}
    
    for iso in isos:
        base_price = random.uniform(20, 80)
        lmp_data[iso] = {
            'average_lmp': round(base_price, 2),
            'min_lmp': round(base_price * 0.5, 2),
            'max_lmp': round(base_price * 1.8, 2),
            'recent_10min_avg': round(base_price * random.uniform(0.9, 1.1), 2),
            'data_points': random.randint(50, 200),
            'latest_timestamp': datetime.now().isoformat(),
            'cheapest_locations': [
                {
                    'location': f'{iso.upper()}_NODE_{i+1}',
                    'lmp': round(base_price * random.uniform(0.3, 0.8), 2),
                    'time': (datetime.now() - timedelta(minutes=random.randint(1, 10))).isoformat()
                }
                for i in range(5)
            ]
        }
    
    return lmp_data

def generate_demo_btc_data():
    """Generate realistic demo BTC data"""
    return {
        'btc_price': random.randint(95000, 105000),
        'network_hashrate_eh': random.randint(580, 620),
        'hashprice_per_th_day': round(random.uniform(0.08, 0.18), 3)
    }

def generate_demo_carbon_data():
    """Generate realistic demo carbon intensity data"""
    regions = ['ercot', 'caiso', 'pjm', 'miso', 'nyiso', 'isone', 'spp', 'ieso']
    carbon_data = {}
    
    for region in regions:
        # California (CAISO) typically cleaner, Texas (ERCOT) mixed, others vary
        if region == 'caiso':
            base_intensity = random.randint(200, 300)
        elif region == 'ercot':
            base_intensity = random.randint(350, 450)
        else:
            base_intensity = random.randint(400, 600)
            
        carbon_data[region] = base_intensity
    
    return carbon_data

def generate_demo_inference_prices():
    """Generate realistic demo inference competition prices"""
    return {
        'competitors': {
            'sfcompute': round(random.uniform(2.0, 2.8), 2),
            'vast_ai': round(random.uniform(1.8, 2.5), 2),
            'runpod': round(random.uniform(2.3, 3.0), 2),
            'lambda_labs': round(random.uniform(2.1, 2.7), 2),
            'coreweave': round(random.uniform(2.5, 3.2), 2),
            'paperspace': round(random.uniform(2.8, 3.5), 2)
        },
        'average': round(random.uniform(2.3, 2.8), 2),
        'lowest': round(random.uniform(1.8, 2.2), 2),
        'highest': round(random.uniform(3.0, 3.5), 2)
    }

def calculate_demo_profit_analysis(lmp_data, btc_data, carbon_data, miner_wth=100):
    """Calculate realistic profit analysis from demo data"""
    results = []
    
    for iso_name, iso_data in lmp_data.items():
        if carbon_data.get(iso_name):
            # Simple profit calculation 
            hashprice_hourly = btc_data['hashprice_per_th_day'] / 24
            electricity_cost_hourly = (miner_wth / 1000) * (iso_data['average_lmp'] / 1000)
            profit_hourly = hashprice_hourly - electricity_cost_hourly
            
            carbon_intensity = carbon_data[iso_name]
            profit_per_carbon = profit_hourly / carbon_intensity * 1000 if carbon_intensity > 0 else 0
            
            results.append({
                'iso': iso_name.upper(),
                'avg_lmp': iso_data['average_lmp'],
                'hourly_profit_per_th': round(profit_hourly, 4),
                'carbon_intensity': carbon_intensity,
                'profit_per_carbon': round(profit_per_carbon, 4),
                'profitable': profit_hourly > 0,
                'miner_efficiency_wth': miner_wth
            })
    
    # Sort by profit per carbon ratio
    results.sort(key=lambda x: x['profit_per_carbon'], reverse=True)
    return results

def generate_demo_hardware_update():
    """Generate demo hardware update"""
    updates = [
        {
            "update": "yes",
            "report": "The Antminer S21 Pro by Bitmain offers exceptional efficiency of 15 W/TH, representing an 85% improvement over the current 100 W/TH standard.",
            "MINER_WTH": 15.0,
            "efficiency_improvement_percent": 85.0
        },
        {
            "update": "yes", 
            "report": "The WhatsMiner M56S++ by MicroBT achieves 22 W/TH efficiency, delivering a 78% improvement over current mining hardware.",
            "MINER_WTH": 22.0,
            "efficiency_improvement_percent": 78.0
        },
        {
            "update": "no",
            "report": "No significant hardware improvements found in recent announcements. Current 100 W/TH remains optimal.",
            "MINER_WTH": 100.0,
            "efficiency_improvement_percent": 0.0
        }
    ]
    
    return random.choice(updates)

def generate_demo_mining_report():
    """Generate demo mining report"""
    reports = [
        "Real-time analysis shows CAISO offers the best profit-to-carbon ratio at $0.0312/kgCO2. Hardware Scout recommends upgrading to Antminer S21 Pro for 85% efficiency gains. Environmental analysis indicates 23% carbon reduction potential through strategic region selection.",
        "Current market conditions favor ERCOT mining with negative pricing opportunities. Carbon arbitrage analysis suggests $0.04/tCO2 additional revenue through voluntary credit markets. Hardware efficiency upgrades could increase profitability by 78%.",
        "Multi-dimensional optimization complete: NYISO provides optimal ESG profile while maintaining $0.0089/TH/hr profitability. Hardware Scout identifies immediate upgrade path. Carbon intensity 35% below national average."
    ]
    
    return {
        'status': 'completed',
        'message': random.choice(reports),
        'timestamp': datetime.now().isoformat()
    }

def save_demo_files():
    """Save demo data to JSON files for dashboard testing"""
    hardware_update = generate_demo_hardware_update()
    mining_report = generate_demo_mining_report()
    
    with open('hardware_update.json', 'w') as f:
        json.dump(hardware_update, f, indent=2)
    
    with open('mining_report.json', 'w') as f:
        json.dump(mining_report, f, indent=2)
    
    print("✅ Demo files created:")
    print("   - hardware_update.json")
    print("   - mining_report.json")

if __name__ == "__main__":
    print("🎭 Generating demo data for MARA Dashboard...")
    
    # Generate and display sample data
    lmp_data = generate_demo_lmp_data()
    btc_data = generate_demo_btc_data()
    carbon_data = generate_demo_carbon_data()
    inference_data = generate_demo_inference_prices()
    profit_analysis = calculate_demo_profit_analysis(lmp_data, btc_data, carbon_data)
    
    print(f"📊 Generated data for {len(lmp_data)} ISOs")
    print(f"💰 BTC Price: ${btc_data['btc_price']:,}")
    print(f"⚡ Best Profit/Carbon: {profit_analysis[0]['iso']} at ${profit_analysis[0]['profit_per_carbon']:.4f}/kgCO2")
    
    # Save demo files
    save_demo_files()
    
    print("\n🚀 Ready for dashboard demo!") 