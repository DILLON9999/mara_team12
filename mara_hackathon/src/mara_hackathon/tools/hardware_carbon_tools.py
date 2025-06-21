"""
Tools for hardware scouting and carbon credit arbitrage
"""
from crewai.tools import BaseTool
from typing import Type, Dict, Any, List
from pydantic import BaseModel, Field
import random
from datetime import datetime, timedelta
import json


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
            },
            {
                "date": (datetime.now() - timedelta(days=3)).isoformat(),
                "source": "Mining Pool Stats",
                "headline": "Foundry USA Now Controls 30% of Bitcoin Hashrate",
                "content": "Consolidation concerns as major pools gain market share",
                "relevant": False
            },
            {
                "date": (datetime.now() - timedelta(days=4)).isoformat(),
                "source": "Tech Insider",
                "headline": "NVIDIA Announces New AI Chips - Not Suitable for Bitcoin Mining",
                "content": "H200 GPUs target AI workloads, not cryptocurrency mining",
                "relevant": False
            },
            {
                "date": (datetime.now() - timedelta(days=8)).isoformat(),
                "source": "Bitmain Support",
                "headline": "Firmware Update 2.3.1 for S19 Series - Bug Fixes Only",
                "content": "Minor stability improvements, no efficiency gains",
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
            },
            # Market noise
            {
                "date": (datetime.now() - timedelta(hours=6)).isoformat(),
                "source": "Bloomberg Green",
                "headline": "Voluntary Carbon Market Sees Record Trading Volume",
                "impact": "Corporate buyers drive demand",
                "relevant": False
            },
            {
                "date": (datetime.now() - timedelta(days=2)).isoformat(),
                "source": "Climate Policy Initiative",
                "headline": "Study: Carbon Credits Need Better Verification",
                "impact": "Quality concerns persist in voluntary markets",
                "relevant": False
            },
            {
                "date": (datetime.now() - timedelta(days=4)).isoformat(),
                "source": "Xpansiv CBL",
                "headline": "Nature-Based Credits Trade at Premium to Tech Solutions",
                "impact": "Forest credits command 20% premium",
                "credit_price_per_tco2": 12.50,
                "relevant": True,
                "region": "Global"
            }
        ]
    
    def get_latest_updates(self, days_back=7):
        """Return carbon market updates from the last N days"""
        cutoff = datetime.now() - timedelta(days=days_back)
        return [item for item in self.market_data 
                if datetime.fromisoformat(item["date"]) > cutoff]


class HardwareScoutTool(BaseTool):
    name: str = "Hardware News Scanner"
    description: str = "Scans latest Bitcoin mining hardware announcements for efficiency improvements"
    
    def _run(self) -> List[Dict[str, Any]]:
        """Fetch latest hardware news"""
        feed = HardwareNewsFeed()
        return feed.get_latest_news(days_back=7)


class CarbonCreditTrackerTool(BaseTool):
    name: str = "Carbon Credit Market Monitor"
    description: str = "Tracks carbon credit prices and policy updates across different markets"
    
    def _run(self) -> List[Dict[str, Any]]:
        """Fetch latest carbon credit market data"""
        market = CarbonCreditMarket()
        return market.get_latest_updates(days_back=7)


class MinerEfficiencyAnalyzerInput(BaseModel):
    """Input for analyzing miner efficiency"""
    current_wth: float = Field(description="Current miner efficiency in W/TH")
    candidate_wth: float = Field(description="Candidate miner efficiency in W/TH")


class MinerEfficiencyAnalyzerTool(BaseTool):
    name: str = "Miner Efficiency Analyzer"
    description: str = "Analyzes if a new miner model offers significant efficiency improvements"
    args_schema: Type[BaseModel] = MinerEfficiencyAnalyzerInput
    
    def _run(self, current_wth: float, candidate_wth: float) -> Dict[str, Any]:
        """Calculate efficiency improvement"""
        improvement_percent = ((current_wth - candidate_wth) / current_wth) * 100
        
        return {
            "current_wth": current_wth,
            "candidate_wth": candidate_wth,
            "improvement_percent": round(improvement_percent, 2),
            "is_significant": improvement_percent >= 5.0,
            "annual_savings_per_th": self._calculate_savings(current_wth, candidate_wth)
        }
    
    def _calculate_savings(self, current_wth: float, new_wth: float) -> float:
        """Calculate annual electricity cost savings per TH"""
        # Assume $0.05/kWh average electricity cost
        kwh_saved_per_hour = (current_wth - new_wth) / 1000
        annual_savings = kwh_saved_per_hour * 24 * 365 * 0.05
        return round(annual_savings, 2)


class CarbonCreditRevenueInput(BaseModel):
    """Input for calculating carbon credit revenue"""
    carbon_saved_tons: float = Field(description="Tons of CO2 saved annually")
    credit_price_per_ton: float = Field(description="Carbon credit price per ton CO2")


class CarbonCreditRevenueTool(BaseTool):
    name: str = "Carbon Credit Revenue Calculator"
    description: str = "Calculates potential revenue from carbon credits based on emissions savings"
    args_schema: Type[BaseModel] = CarbonCreditRevenueInput
    
    def _run(self, carbon_saved_tons: float, credit_price_per_ton: float) -> Dict[str, Any]:
        """Calculate carbon credit revenue potential"""
        annual_revenue = carbon_saved_tons * credit_price_per_ton
        
        return {
            "carbon_saved_tons": carbon_saved_tons,
            "credit_price_per_ton": credit_price_per_ton,
            "annual_revenue": round(annual_revenue, 2),
            "monthly_revenue": round(annual_revenue / 12, 2),
            "daily_revenue": round(annual_revenue / 365, 2)
        } 