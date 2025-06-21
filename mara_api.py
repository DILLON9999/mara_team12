import requests
import json

# Base API URL
BASE_URL = "https://mara-hackathon-api.onrender.com"

def get_inventory():
    """Get available inventory/resources from Mara API"""
    try:
        response = requests.get(f"{BASE_URL}/inventory")
        return response.json()
    except Exception as e:
        print(f"Error getting inventory: {e}")
        return None

def allocate_machines(api_key, air_miners=0, hydro_miners=0, immersion_miners=0, 
                     gpu_compute=0, asic_compute=0):
    """Allocate machines using Mara API"""
    try:
        headers = {"X-Api-Key": api_key}
        data = {
            "air_miners": air_miners,
            "hydro_miners": hydro_miners, 
            "immersion_miners": immersion_miners,
            "gpu_compute": gpu_compute,
            "asic_compute": asic_compute
        }
        
        response = requests.put(f"{BASE_URL}/machines", headers=headers, json=data)
        return response.json()
    except Exception as e:
        print(f"Error allocating machines: {e}")
        return None

def get_current_status(api_key):
    """Get current machine allocation and performance"""
    try:
        headers = {"X-Api-Key": api_key}
        response = requests.get(f"{BASE_URL}/machines", headers=headers)
        return response.json()
    except Exception as e:
        print(f"Error getting status: {e}")
        return None

# Test the functions
if __name__ == "__main__":
    # Test inventory
    print("=== INVENTORY ===")
    inventory = get_inventory()
    if inventory:
        print(f"GPU inference: {inventory['inference']['gpu']['tokens']} tokens, {inventory['inference']['gpu']['power']} power")
        print(f"Immersion miners: {inventory['miners']['immersion']['hashrate']} hashrate, {inventory['miners']['immersion']['power']} power")
    
    # You'll need to use your actual API key here
    api_key = "your-api-key-here"
    
    print(f"\n=== CURRENT STATUS ===")
    status = get_current_status(api_key)
    if status:
        print(f"Total power used: {status.get('total_power_used', 0):,}")
        print(f"Total revenue: ${status.get('total_revenue', 0):,.2f}")
        print(f"Power cost: ${status.get('total_power_cost', 0):,.2f}")
        print(f"Net profit: ${status.get('total_revenue', 0) - status.get('total_power_cost', 0):,.2f}") 