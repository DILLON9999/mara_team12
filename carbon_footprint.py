import os
import time
import csv
import datetime
import pandas as pd
from gridstatus import Ercot, SPP, NYISO, ISONE, IESO
import ssl
import urllib.request

ssl._create_default_https_context = ssl._create_unverified_context


# Set your PJM API key (if needed)

CARBON_FACTORS = {
    "coal": 1000, "natural gas": 450, "nuclear": 0,
    "wind": 0, "solar": 0, "hydro": 4, "biomass": 230,
    "battery": 0, "geothermal": 45, "other": 500
}

isos = {
    "ercot": Ercot(),
    "spp": SPP(),
    "nyiso": NYISO(),
    "isone": ISONE(),
    "ieso": IESO()
}

def fetch_fuel_mix(region_obj, region_name):
    try:
        today = datetime.date.today()
        df = region_obj.get_fuel_mix(date=today)
        print(f"✅ Logged {region_name}")
        return df
    except Exception as e:
        import traceback
        print(f"❌ Error logging {region_name}: {type(e).__name__} - {e}")
        traceback.print_exc()
        return None


def calculate_carbon_intensity(df):
    emissions_factors = {
        "Coal": 1001,
        "Natural Gas": 469,
        "Oil": 840,
        "Nuclear": 0,
        "Wind": 0,
        "Solar": 0,
        "Hydro": 0,
        "Battery": 0,
        "Other": 300,
    }

    total_gen = df["value"].sum()
    total_emissions = 0.0

    for _, row in df.iterrows():
        fuel = str(row["fuel"]).title()
        value = row["value"]
        emission = emissions_factors.get(fuel, 300)
        total_emissions += emission * value

    return round(total_emissions / total_gen, 2) if total_gen > 0 else 0


def write_to_csv(df, region_key):
    if df is None or df.empty:
        print(f"⚠️ Skipping empty data for {region_key}")
        return

    timestamp = datetime.datetime.now().isoformat()

    # Find fuel columns (exclude time/date columns)
    time_cols = [col for col in df.columns if "time" in col.lower() or "date" in col.lower()]
    fuel_cols = [col for col in df.columns if col not in time_cols]

    # Melt to long format: fuel, value
    df_melted = df[fuel_cols].iloc[-1:].melt(var_name="fuel", value_name="value")

    # Clean and convert
    df_melted["fuel"] = df_melted["fuel"].str.strip().str.title()
    df_melted = df_melted[pd.to_numeric(df_melted["value"], errors="coerce").notnull()].copy()
    df_melted["value"] = df_melted["value"].astype(float)

    # Calculate carbon intensity
    intensity = calculate_carbon_intensity(df_melted)

    # Save row
    row = [timestamp] + df_melted["value"].tolist() + [intensity]
    headers = ["timestamp"] + df_melted["fuel"].tolist() + ["carbon_intensity"]

    # Write to CSV
    filename = f"{region_key}_fuel_mix.csv"
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)

    print(f"✅ Logged {region_key.upper()}")

def run_logger():
    while True:
        for region_key, iso in isos.items():
            df = fetch_fuel_mix(iso, region_key)
            if df is not None and not df.empty:
                print(f"✅ Logged {region_key.upper()}")
                write_to_csv(df, region_key)
        print("⏳ Waiting 5 minutes...\n")
        time.sleep(300)

if __name__ == "__main__":
    run_logger()