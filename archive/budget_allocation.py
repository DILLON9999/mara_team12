import requests
import json

def get_inventory():
    """Get machine types and their power costs"""
    response = requests.get("https://mara-hackathon-api.onrender.com/inventory")
    return response.json()

def calculate_power_budget(air_miners=0, hydro_miners=0, immersion_miners=0, 
                          gpu_compute=0, asic_compute=0):
    """Calculate total power budget needed for allocation"""
    inventory = get_inventory()
    
    total_power = (
        air_miners * inventory['miners']['air']['power'] +
        hydro_miners * inventory['miners']['hydro']['power'] +
        immersion_miners * inventory['miners']['immersion']['power'] +
        gpu_compute * inventory['inference']['gpu']['power'] +
        asic_compute * inventory['inference']['asic']['power']
    )
    
    return total_power

def optimize_allocation_for_budget(strategy="inference", max_budget=1000000):
    """Optimize allocation within power budget"""
    inventory = get_inventory()
    
    if strategy == "inference":
        # Prioritize inference with budget constraints
        
        # GPU inference is more power-efficient (3333 power for 1000 tokens)
        # ASIC inference is less efficient (10000 power for 5000 tokens)
        
        max_gpu = max_budget // inventory['inference']['gpu']['power']
        remaining_budget = max_budget - (max_gpu * inventory['inference']['gpu']['power'])
        max_asic = remaining_budget // inventory['inference']['asic']['power']
        
        return {
            "air_miners": 0,
            "hydro_miners": 0, 
            "immersion_miners": 0,
            "gpu_compute": max_gpu,
            "asic_compute": max_asic,
            "total_power_used": calculate_power_budget(0, 0, 0, max_gpu, max_asic),
            "strategy": "MAX_INFERENCE"
        }
    
    elif strategy == "mining":
        # Prioritize mining - hydro has best hashrate/power ratio
        
        max_hydro = max_budget // inventory['miners']['hydro']['power']
        remaining_budget = max_budget - (max_hydro * inventory['miners']['hydro']['power'])
        max_air = remaining_budget // inventory['miners']['air']['power']
        
        return {
            "air_miners": max_air,
            "hydro_miners": max_hydro,
            "immersion_miners": 0,
            "gpu_compute": 0,
            "asic_compute": 0,
            "total_power_used": calculate_power_budget(max_air, max_hydro, 0, 0, 0),
            "strategy": "MAX_MINING"
        }
    
    elif strategy == "mixed":
        # 50/50 split between mining and inference
        half_budget = max_budget // 2
        
        # Mining allocation (first half)
        max_hydro = half_budget // inventory['miners']['hydro']['power']
        mining_used = max_hydro * inventory['miners']['hydro']['power']
        
        # Inference allocation (second half) 
        inference_budget = max_budget - mining_used
        max_gpu = inference_budget // inventory['inference']['gpu']['power']
        
        return {
            "air_miners": 0,
            "hydro_miners": max_hydro,
            "immersion_miners": 0, 
            "gpu_compute": max_gpu,
            "asic_compute": 0,
            "total_power_used": calculate_power_budget(0, max_hydro, 0, max_gpu, 0),
            "strategy": "MIXED_50_50"
        }

def show_allocation_options():
    """Show different allocation strategies within budget"""
    print("=== POWER BUDGET ALLOCATION OPTIONS ===")
    print("Budget: 1,000,000 power units\n")
    
    strategies = ["inference", "mining", "mixed"]
    
    for strategy in strategies:
        allocation = optimize_allocation_for_budget(strategy)
        print(f"{allocation['strategy']}:")
        print(f"  Air miners: {allocation['air_miners']}")
        print(f"  Hydro miners: {allocation['hydro_miners']}")  
        print(f"  Immersion miners: {allocation['immersion_miners']}")
        print(f"  GPU compute: {allocation['gpu_compute']}")
        print(f"  ASIC compute: {allocation['asic_compute']}")
        print(f"  Power used: {allocation['total_power_used']:,} / 1,000,000")
        print(f"  Power remaining: {1000000 - allocation['total_power_used']:,}")
        print()

if __name__ == "__main__":
    show_allocation_options() 