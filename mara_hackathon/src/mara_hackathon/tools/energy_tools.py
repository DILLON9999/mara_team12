"""
Custom tools for energy market analysis and Bitcoin mining optimization
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))

from crewai.tools import BaseTool
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
from proj.inputs import (
    get_cheapest_lmp,
    get_btc_hashprice,
    get_carbon_intensity_by_iso,
    calculate_hourly_mining_profit,
    calculate_profit_per_carbon_intensity,
    get_inference_competition_prices
)


class LMPAnalyzerInput(BaseModel):
    """Input schema for LMP Analyzer"""
    num_locations: int = Field(default=5, description="Number of cheapest locations to return per ISO")


class LMPAnalyzerTool(BaseTool):
    name: str = "LMP Analyzer"
    description: str = "Fetches real-time LMP (Locational Marginal Pricing) data from all major ISOs"
    args_schema: Type[BaseModel] = LMPAnalyzerInput
    
    def _run(self, num_locations: int = 5) -> Dict[str, Any]:
        """Fetch LMP data from all ISOs"""
        return get_cheapest_lmp(num_locations)


class BTCHashpriceTool(BaseTool):
    name: str = "Bitcoin Hashprice Monitor"
    description: str = "Gets current Bitcoin price and mining hashprice metrics"
    
    def _run(self) -> Dict[str, Any]:
        """Fetch current BTC hashprice data"""
        return get_btc_hashprice()


class CarbonIntensityTool(BaseTool):
    name: str = "Carbon Intensity Tracker"
    description: str = "Fetches real-time carbon intensity data for each ISO based on current fuel mix"
    
    def _run(self) -> Dict[str, Any]:
        """Get carbon intensity by ISO with enhanced ERCOT handling"""
        from datetime import datetime, timedelta
        from gridstatus import Ercot, SPP, NYISO, ISONE
        try:
            from gridstatus import IESO
        except ImportError:
            IESO = None
        import pandas as pd
        
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
        
        print("Fetching carbon intensity data from ISOs...")
        
        isos = {
            "ercot": Ercot(),
            "spp": SPP(),
            "nyiso": NYISO(),
            "isone": ISONE()
        }
        
        # Add IESO if available
        if IESO is not None:
            isos["ieso"] = IESO()
        
        carbon_intensities = {}
        
        for region_key, iso in isos.items():
            try:
                # Get today's fuel mix with special ERCOT handling
                today = datetime.now().date()
                
                if region_key == "ercot":
                    # Try multiple approaches for ERCOT
                    df = None
                    for days_back in range(3):  # Try today, yesterday, day before
                        try:
                            target_date = today - timedelta(days=days_back)
                            df = iso.get_fuel_mix(date=target_date)
                            if df is not None and not df.empty:
                                if days_back > 0:
                                    print(f"  ERCOT: Using data from {days_back} day(s) ago due to timezone issues")
                                break
                        except Exception as e:
                            if days_back == 2:  # Last attempt failed
                                print(f"  ERCOT: All date attempts failed: {str(e)}")
                            continue
                else:
                    df = iso.get_fuel_mix(date=today)
                
                if df is not None and not df.empty:
                    # Get the most recent data
                    latest_row = df.iloc[-1]
                    
                    # Calculate total generation and emissions
                    total_gen = 0
                    total_emissions = 0
                    
                    # Define columns to exclude (timestamp/datetime columns)
                    exclude_cols = ['Time', 'time', 'datetime', 'interval_start', 'interval_end', 
                                   'interval_start_utc', 'interval_end_utc', 'publish_time', 
                                   'timestamp', 'date', 'hour']
                    
                    for col in df.columns:
                        if col not in exclude_cols:
                            try:
                                # Check if the value can be converted to float
                                raw_value = latest_row[col]
                                if pd.notna(raw_value):
                                    # Try to convert to numeric, skip if it's a timestamp/string
                                    if isinstance(raw_value, (int, float)):
                                        value = float(raw_value)
                                    elif isinstance(raw_value, str):
                                        try:
                                            value = float(raw_value)
                                        except ValueError:
                                            # Skip non-numeric strings
                                            continue
                                    else:
                                        # Skip datetime/timestamp objects
                                        continue
                                else:
                                    value = 0
                                
                                # Map fuel type to carbon factor
                                fuel_type = col.lower()
                                emission_factor = CARBON_FACTORS.get(fuel_type, 300)
                                
                                total_gen += value
                                total_emissions += emission_factor * value
                                
                            except (ValueError, TypeError):
                                # Skip columns that can't be converted to float
                                continue
                    
                    # Calculate carbon intensity (gCO2/MWh)
                    if total_gen > 0:
                        carbon_intensity = round(total_emissions / total_gen, 2)
                        carbon_intensities[region_key] = carbon_intensity
                        print(f"  {region_key.upper()}: {carbon_intensity} gCO2/MWh")
                    else:
                        # Use regional estimates if no valid generation data
                        region_defaults = {
                            'ercot': 400,  # Texas grid (gas/wind mix)
                            'spp': 500,   # Midwest grid (coal/gas/wind mix)
                            'nyiso': 300, # NY grid (gas/hydro/nuclear mix)
                            'isone': 250  # New England grid (gas/nuclear/renewables)
                        }
                        carbon_intensities[region_key] = region_defaults.get(region_key, 500)
                        print(f"  {region_key.upper()}: {carbon_intensities[region_key]} gCO2/MWh (estimated)")
                else:
                    carbon_intensities[region_key] = None
                    print(f"  {region_key.upper()}: No data available")
                    
            except Exception as e:
                print(f"  Error fetching {region_key}: {str(e)}")
                # Use regional estimates for problematic regions
                region_defaults = {
                    'ercot': 400,  # Texas grid (gas/wind mix)
                    'spp': 500,   # Midwest grid (coal/gas/wind mix)
                    'nyiso': 300, # NY grid (gas/hydro/nuclear mix)
                    'isone': 250  # New England grid (gas/nuclear/renewables)
                }
                carbon_intensities[region_key] = region_defaults.get(region_key, 500)
                print(f"  {region_key.upper()}: {carbon_intensities[region_key]} gCO2/MWh (default estimate)")
        
        # Add estimates for CAISO, MISO, PJM (not available via gridstatus)
        carbon_intensities['caiso'] = 250  # California typically cleaner
        carbon_intensities['miso'] = 600   # Mixed coal/gas
        carbon_intensities['pjm'] = 550    # Mixed coal/gas/nuclear
        
        return carbon_intensities


class MiningProfitInput(BaseModel):
    """Input schema for Mining Profit Calculator"""
    lmp_per_mwh: float = Field(description="Electricity price in $/MWh")
    hashprice_per_th_day: float = Field(description="Bitcoin mining revenue in $/TH/day")
    miner_efficiency_watts_per_th: int = Field(default=100, description="Power consumption in watts per TH/s")


class MiningProfitCalculatorTool(BaseTool):
    name: str = "Mining Profit Calculator"
    description: str = "Calculates hourly Bitcoin mining profitability given electricity costs"
    args_schema: Type[BaseModel] = MiningProfitInput
    
    def _run(self, lmp_per_mwh: float, hashprice_per_th_day: float, 
             miner_efficiency_watts_per_th: int = 100) -> Dict[str, Any]:
        """Calculate mining profitability"""
        return calculate_hourly_mining_profit(
            lmp_per_mwh, 
            hashprice_per_th_day, 
            miner_efficiency_watts_per_th
        )


class ProfitCarbonAnalyzerInput(BaseModel):
    """Input schema for Profit/Carbon Analyzer"""
    custom_miner_wth: float = Field(default=100.0, description="Custom miner efficiency in W/TH (defaults to 100 W/TH)")


class ProfitCarbonAnalyzerTool(BaseTool):
    name: str = "Profit/Carbon Ratio Analyzer"
    description: str = "Calculates profit per carbon intensity ratios for all regions"
    args_schema: Type[BaseModel] = ProfitCarbonAnalyzerInput
    
    def _run(self, custom_miner_wth: float = 100.0) -> list:
        """Calculate profit/carbon ratios for all ISOs"""
        # First get all required data
        lmp_data = get_cheapest_lmp()
        btc_data = get_btc_hashprice()
        carbon_data = get_carbon_intensity_by_iso()
        
        # Calculate profit/carbon ratios with custom efficiency
        return calculate_profit_per_carbon_intensity(lmp_data, btc_data, carbon_data, custom_miner_wth)


class InferenceMarketTool(BaseTool):
    name: str = "Inference Market Monitor"
    description: str = "Gets current H100 GPU inference pricing from major providers"
    
    def _run(self) -> Dict[str, Any]:
        """Get inference competition prices"""
        return get_inference_competition_prices()


class DashboardPublisherInput(BaseModel):
    """Input schema for Dashboard Publisher"""
    api_endpoint: str = Field(description="API endpoint URL to post data")
    data: Dict[str, Any] = Field(description="Data to publish to dashboard")


class DashboardPublisherTool(BaseTool):
    name: str = "Dashboard Publisher"
    description: str = "Publishes analysis results to external dashboard API"
    args_schema: Type[BaseModel] = DashboardPublisherInput
    
    def _run(self, api_endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Publish data to dashboard (placeholder for now)"""
        # In production, this would make actual API calls
        import json
        import datetime
        
        # Format the data with timestamp
        formatted_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "data": data,
            "status": "published"
        }
        
        # Log what would be sent
        print(f"Would POST to {api_endpoint}:")
        print(json.dumps(formatted_data, indent=2))
        
        return {
            "success": True,
            "endpoint": api_endpoint,
            "data_size": len(json.dumps(data)),
            "timestamp": formatted_data["timestamp"]
        } 