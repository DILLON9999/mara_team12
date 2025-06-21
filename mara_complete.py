import requests
import json
from datetime import datetime, timedelta
from gridstatusio import GridStatusClient

# Generate site and get API key (from original script)
def generate_new_site(site_name="mara_hackathon"):
    url = "https://mara-hackathon-api.onrender.com/sites"
    payload = json.dumps({"name": site_name})
    headers = {'Content-Type': 'application/json'}
    
    response = requests.request("POST", url, headers=headers, data=payload)
    response_data = json.loads(response.text)
    
    return {
        "power": response_data["power"],
        "api_key": response_data["api_key"]
    }

# Mara API functions
def get_inventory():
    """Get available inventory/resources from Mara API"""
    response = requests.get("https://mara-hackathon-api.onrender.com/inventory")
    return response.json()

def allocate_machines(api_key, air_miners=0, hydro_miners=0, immersion_miners=0, 
                     gpu_compute=0, asic_compute=0):
    """Allocate machines using Mara API"""
    headers = {"X-Api-Key": api_key}
    data = {
        "air_miners": air_miners,
        "hydro_miners": hydro_miners, 
        "immersion_miners": immersion_miners,
        "gpu_compute": gpu_compute,
        "asic_compute": asic_compute
    }
    
    response = requests.put("https://mara-hackathon-api.onrender.com/machines", 
                           headers=headers, json=data)
    
    print(f"Allocation response code: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Allocation error: {response.status_code} - {response.text}")
        return None

def get_current_status(api_key):
    """Get current machine allocation and performance"""
    headers = {"X-Api-Key": api_key}
    response = requests.get("https://mara-hackathon-api.onrender.com/machines", headers=headers)
    
    print(f"Status response code: {response.status_code}")
    print(f"Status response text: {response.text[:200]}...")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Market data functions (simplified)
def get_cheapest_lmp():
    """Get cheapest LMP price in ERCOT"""
    client = GridStatusClient("03f45cf6cd074c348c3669836544dbe6")
    
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=15)
    
    df = client.get_dataset(
        dataset="ercot_lmp_by_settlement_point",
        start=start_time.strftime("%Y-%m-%d %H:%M"),
        end=end_time.strftime("%Y-%m-%d %H:%M"),
        timezone="market",
    )
    
    if not df.empty:
        latest_time = df['interval_start_utc'].max()
        latest_df = df[df['interval_start_utc'] == latest_time]
        cheapest = latest_df.nsmallest(1, 'lmp').iloc[0]
        return cheapest['lmp']
    return 50  # Default fallback

# Simple allocation strategy
def calculate_optimal_allocation(api_key, lmp_price):
    """Calculate optimal allocation based on current market conditions"""
    
    # Get current inventory
    inventory = get_inventory()
    
    # Simple decision logic
    if lmp_price < 0:
        # Negative pricing - run everything for inference
        recommendation = {
            "strategy": "MAX_INFERENCE_NEGATIVE_ENERGY",
            "air_miners": 0,
            "hydro_miners": 0,
            "immersion_miners": 0,
            "gpu_compute": 100,  # Max GPU inference
            "asic_compute": 50   # Max ASIC inference
        }
    elif lmp_price < 20:
        # Cheap energy - favor inference
        recommendation = {
            "strategy": "INFERENCE_FOCUS", 
            "air_miners": 0,
            "hydro_miners": 0,
            "immersion_miners": 20,  # Some mining
            "gpu_compute": 80,       # Mostly inference
            "asic_compute": 30
        }
    else:
        # Expensive energy - focus on mining
        recommendation = {
            "strategy": "MINING_FOCUS",
            "air_miners": 10,
            "hydro_miners": 30,
            "immersion_miners": 40,
            "gpu_compute": 20,
            "asic_compute": 10
        }
    
    return recommendation

# Main execution
if __name__ == "__main__":
    print("=== MARA REAL-TIME ALLOCATION SYSTEM ===")
    
    # 1. Generate site and get API key
    site_info = generate_new_site()
    api_key = site_info["api_key"]
    print(f"Generated site with API key: {api_key[:8]}...")
    
    # 2. Get current market conditions
    print("\nGetting current market data...")
    lmp_price = get_cheapest_lmp()
    print(f"Cheapest LMP: ${lmp_price}/MWh")
    
    # 3. Calculate optimal allocation
    allocation = calculate_optimal_allocation(api_key, lmp_price)
    print(f"\nStrategy: {allocation['strategy']}")
    
    # 4. Get current status before allocation
    print("\n--- BEFORE ALLOCATION ---")
    status_before = get_current_status(api_key)
    if status_before:
        print(f"Current revenue: ${status_before.get('total_revenue', 0):,.2f}")
        print(f"Current power cost: ${status_before.get('total_power_cost', 0):,.2f}")
    
    # 5. Make the allocation
    print(f"\nAllocating machines...")
    allocation_result = allocate_machines(
        api_key,
        air_miners=allocation["air_miners"],
        hydro_miners=allocation["hydro_miners"], 
        immersion_miners=allocation["immersion_miners"],
        gpu_compute=allocation["gpu_compute"],
        asic_compute=allocation["asic_compute"]
    )
    
    # 6. Check new status
    print("\n--- AFTER ALLOCATION ---")
    status_after = get_current_status(api_key)
    if status_after:
        print(f"New revenue: ${status_after.get('total_revenue', 0):,.2f}")
        print(f"New power cost: ${status_after.get('total_power_cost', 0):,.2f}")
        print(f"Net profit: ${status_after.get('total_revenue', 0) - status_after.get('total_power_cost', 0):,.2f}")
        
        print(f"\nAllocation breakdown:")
        print(f"  Mining: {status_after.get('air_miners', 0) + status_after.get('hydro_miners', 0) + status_after.get('immersion_miners', 0)} total miners")
        print(f"  Inference: {status_after.get('gpu_compute', 0)} GPU + {status_after.get('asic_compute', 0)} ASIC") 