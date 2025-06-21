#!/usr/bin/env python
"""
Test script to demonstrate Hardware Scout and Carbon Arbitrageur agents
"""
from datetime import datetime, timedelta

# Simulated tools that would normally come from hardware_carbon_tools
class HardwareNewsFeed:
    """Simulated hardware news feed with realistic-looking data"""
    
    def __init__(self):
        self.current_miner_wth = 100  # Current efficiency baseline
        
        # Mix of relevant and irrelevant news
        self.news_items = [
            # Relevant hardware news
            {
                "date": (datetime.now() - timedelta(days=2)).isoformat(),
                "source": "Bitmain Official",
                "headline": "Bitmain Announces S21 XP Hydro - 85 J/TH Efficiency",
                "content": "Revolutionary liquid cooling achieves 85 watts per terahash, 15% improvement over current gen",
                "efficiency_wth": 85,
                "model": "Antminer S21 XP Hydro",
                "relevant": True
            },
            {
                "date": (datetime.now() - timedelta(days=5)).isoformat(),
                "source": "MicroBT Press Release",
                "headline": "WhatsMiner M56S++ Reaches 22 J/TH in Lab Tests",
                "content": "Ultra-efficient chip design achieves breakthrough 22 J/TH efficiency in optimal conditions",
                "efficiency_wth": 22,
                "model": "WhatsMiner M56S++",
                "relevant": True
            },
            {
                "date": (datetime.now() - timedelta(days=7)).isoformat(),
                "source": "AsicMinerValue.com",
                "headline": "Canaan AvalonMiner 1466 Review: Solid but Not Revolutionary",
                "content": "New model delivers 150 TH/s at 3230W, achieving 21.5 J/TH efficiency",
                "efficiency_wth": 21.5,
                "model": "AvalonMiner 1466",
                "relevant": True
            },
            # Irrelevant news (distractors)
            {
                "date": (datetime.now() - timedelta(days=1)).isoformat(),
                "source": "CryptoNews Daily",
                "headline": "Bitcoin Surges Past $100K as ETF Inflows Accelerate",
                "content": "Market analysis shows institutional adoption driving prices",
                "relevant": False
            }
        ]

    def get_latest_news(self, days_back=7):
        """Return news from the last N days"""
        cutoff = datetime.now() - timedelta(days=days_back)
        return [item for item in self.news_items 
                if datetime.fromisoformat(item["date"]) > cutoff]


class CarbonCreditMarket:
    """Simulated carbon credit market data"""
    
    def __init__(self):
        self.market_data = [
            # Significant policy changes
            {
                "date": (datetime.now() - timedelta(hours=12)).isoformat(),
                "source": "US Treasury",
                "headline": "45Q Tax Credit Increased to $85/tCO2 for Direct Air Capture",
                "impact": "Major boost for carbon capture projects",
                "credit_price_per_tco2": 85,
                "relevant": True,
                "region": "US"
            },
            {
                "date": (datetime.now() - timedelta(days=1)).isoformat(),
                "source": "California ARB",
                "headline": "California Carbon Allowances Hit Record $41.50/tCO2",
                "impact": "Cap-and-trade prices surge on tight supply",
                "credit_price_per_tco2": 41.50,
                "relevant": True,
                "region": "CAISO"
            },
            {
                "date": (datetime.now() - timedelta(days=3)).isoformat(),
                "source": "EU Commission",
                "headline": "EU ETS Prices Stabilize at €95/tCO2",
                "impact": "European carbon market finds equilibrium",
                "credit_price_per_tco2": 103.85,  # EUR to USD
                "relevant": True,
                "region": "EU"
            }
        ]
    
    def get_latest_updates(self, days_back=7):
        """Return carbon market updates from the last N days"""
        cutoff = datetime.now() - timedelta(days=days_back)
        return [item for item in self.market_data 
                if datetime.fromisoformat(item["date"]) > cutoff]

def analyze_efficiency(current_wth, candidate_wth):
    """Calculate efficiency improvement"""
    improvement_percent = ((current_wth - candidate_wth) / current_wth) * 100
    
    # Calculate annual electricity cost savings per TH
    kwh_saved_per_hour = (current_wth - candidate_wth) / 1000
    annual_savings = kwh_saved_per_hour * 24 * 365 * 0.05
    
    return {
        "current_wth": current_wth,
        "candidate_wth": candidate_wth,
        "improvement_percent": round(improvement_percent, 2),
        "is_significant": improvement_percent >= 5.0,
        "annual_savings_per_th": round(annual_savings, 2)
    }

def calculate_carbon_revenue(carbon_saved_tons, credit_price_per_ton):
    """Calculate carbon credit revenue potential"""
    annual_revenue = carbon_saved_tons * credit_price_per_ton
    
    return {
        "carbon_saved_tons": carbon_saved_tons,
        "credit_price_per_ton": credit_price_per_ton,
        "annual_revenue": round(annual_revenue, 2),
        "monthly_revenue": round(annual_revenue / 12, 2),
        "daily_revenue": round(annual_revenue / 365, 2)
    }

def test_hardware_scout():
    print("=== HARDWARE SCOUT DEMO ===\n")
    
    # Get hardware news
    feed = HardwareNewsFeed()
    news = feed.get_latest_news()
    
    # Current efficiency
    current_wth = 100
    print(f"Current miner efficiency: {current_wth} W/TH\n")
    
    # Analyze each hardware announcement
    for item in news:
        if item.get('relevant', False):
            print(f"📰 {item['headline']}")
            print(f"   Source: {item['source']}")
            print(f"   Date: {item['date'][:10]}")
            
            if 'efficiency_wth' in item:
                result = analyze_efficiency(
                    current_wth=current_wth,
                    candidate_wth=item['efficiency_wth']
                )
                
                print(f"   Efficiency: {item['efficiency_wth']} W/TH")
                print(f"   Improvement: {result['improvement_percent']}%")
                print(f"   Significant: {'✅ YES' if result['is_significant'] else '❌ NO'}")
                print(f"   Annual savings per TH: ${result['annual_savings_per_th']}")
                
                if result['is_significant']:
                    print(f"\n   🎯 RECOMMENDATION: Upgrade to {item.get('model', 'this model')}")
                    print(f"   This would save {result['improvement_percent']}% on electricity costs!")
            print()

def test_carbon_arbitrageur():
    print("\n=== CARBON ARBITRAGEUR DEMO ===\n")
    
    # Get carbon credit market data
    market = CarbonCreditMarket()
    updates = market.get_latest_updates()
    
    # Simulate mining operation
    print("Scenario: 1000 TH/s mining operation\n")
    
    # Example carbon savings by switching regions
    # MISO (600 gCO2/MWh) to CAISO (250 gCO2/MWh)
    miso_carbon = 600  # gCO2/MWh
    caiso_carbon = 250  # gCO2/MWh
    power_consumption_mw = 0.1  # 100 kW for 1000 TH/s at 100 W/TH
    hours_per_year = 8760
    
    carbon_saved_g = (miso_carbon - caiso_carbon) * power_consumption_mw * hours_per_year
    carbon_saved_tons = carbon_saved_g / 1_000_000  # Convert to tons
    
    print(f"Carbon saved by moving from MISO to CAISO: {carbon_saved_tons:.2f} tons CO2/year\n")
    
    # Analyze carbon credit opportunities
    carbon_events = []
    
    for update in updates:
        if update.get('relevant', False) and 'credit_price_per_tco2' in update:
            print(f"💹 {update['headline']}")
            print(f"   Source: {update['source']}")
            print(f"   Region: {update.get('region', 'Global')}")
            print(f"   Price: ${update['credit_price_per_tco2']}/tCO2")
            
            # Calculate revenue potential
            revenue = calculate_carbon_revenue(
                carbon_saved_tons=carbon_saved_tons,
                credit_price_per_ton=update['credit_price_per_tco2']
            )
            
            print(f"   Annual revenue potential: ${revenue['annual_revenue']:,.2f}")
            print(f"   Daily revenue: ${revenue['daily_revenue']:.2f}")
            
            # Add to events list
            carbon_events.append((
                update['date'],
                update['headline'],
                revenue['annual_revenue'] / 1000  # Convert to per TH metric
            ))
            print()
    
    print("\n📊 Carbon Events Summary:")
    print("carbon_events = [")
    for event in carbon_events:
        print(f'  ("{event[0]}", "{event[1]}", {event[2]:.3f}),')
    print("]")
    
    print("\n💡 RECOMMENDATION:")
    print("California's $41.50/tCO2 carbon price makes CAISO even more attractive.")
    print(f"Moving 1000 TH/s from MISO to CAISO could generate ${carbon_saved_tons * 41.50:,.2f}")
    print("in additional annual revenue from carbon credits alone!")

if __name__ == "__main__":
    test_hardware_scout()
    test_carbon_arbitrageur() 