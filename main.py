import requests
import json
from datetime import datetime, timedelta

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
    # Generate timestamps - current time and one hour ago
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)
    
    # Format timestamps in ISO format with Z suffix
    start_timestamp = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_timestamp = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    url = f"https://api.gridstatus.io/v1/datasets/{region}/query?start={start_timestamp}&end={end_timestamp}&limit=5000"
    
    payload = {}
    headers = {
        'X-Api-Key': '03f45cf6cd074c348c3669836544dbe6'
    }
    
    response = requests.request("GET", url, headers=headers, data=payload)
    
    return response.text

def find_lowest_lmp_locations():
    """Query all regions and find the 5 locations with the lowest LMP prices"""
    all_lmp_data = []
    
    for region in regions:
        print(f"Querying region: {region}")
        try:
            response_text = query_grid_data(region)
            response_data = json.loads(response_text)
            
            if response_data.get("status_code") == 200 and "data" in response_data:
                for item in response_data["data"]:
                    if "lmp" in item and "location" in item:
                        all_lmp_data.append({
                            "region": region,
                            "location": item["location"],
                            "lmp": item["lmp"],
                            "interval_start_utc": item.get("interval_start_utc", ""),
                            "market": item.get("market", "")
                        })
            else:
                print(f"Error querying {region}: {response_data}")
        except Exception as e:
            print(f"Error processing {region}: {str(e)}")
    
    # Sort by LMP price and get the 5 lowest
    lowest_lmp = sorted(all_lmp_data, key=lambda x: x["lmp"])[:5]
    
    return lowest_lmp

regions = ["ercot_lmp_by_settlement_point", "caiso_rt5m_lmp_by_node", "pjm_rt_lmp_by_pnode", "spp_rt5m_lmp_by_resource", "miso_rt_lmp_by_node", "nyiso_rt_lmp_by_zone"]

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
