# Energy-Bitcoin Mining Optimization Crew 🌊⚡️₿

An intelligent multi-agent system that continuously monitors energy markets and Bitcoin mining profitability to optimize mining operations for maximum profit per carbon emission.

## Overview

This CrewAI-powered system uses specialized agents to:
- 📊 Monitor real-time electricity prices (LMP) across all major ISOs
- 🌱 Track carbon intensity of power grids
- 💰 Calculate Bitcoin mining profitability
- 🎯 Optimize mining locations for best profit/carbon ratios
- 📈 Publish insights to dashboards

## Agents

### 1. Market Intelligence Agent
- Monitors LMP prices across ERCOT, CAISO, NYISO, ISONE, IESO, MISO, PJM, SPP
- Tracks Bitcoin price and hashprice
- Identifies negative pricing events

### 2. Environmental Analyst
- Calculates real-time carbon intensity for each ISO
- Tracks fuel mix (coal, gas, nuclear, renewables)
- Provides ESG metrics

### 3. Hardware Scout
- Scans Bitcoin mining hardware announcements from Bitmain, MicroBT, Canaan
- Identifies miners with >5% efficiency improvements
- Outputs structured JSON recommendations for hardware upgrades

### 4. Optimization Strategist
- Calculates profit per carbon ratios
- Makes mining location recommendations
- Determines optimal mining intensity
- Incorporates hardware efficiency updates

### 5. Carbon Arbitrageur
- Tracks carbon credit prices (45Q, EU ETS, California ARB)
- Analyzes policy changes affecting carbon markets
- Recommends hashrate reallocation based on carbon credit opportunities
- Maintains event log of significant market developments

### 6. Dashboard Publisher
- Formats data for external APIs
- Generates alerts for exceptional opportunities
- Creates executive summaries
- Includes hardware and carbon credit recommendations

## Installation

```bash
# Install dependencies
pip install crewai crewai-tools gridstatusio gridstatus pandas requests

# Navigate to the project
cd proj/mara_hackathon
```

## Usage

### Single Run
```bash
# Run once
cd src/mara_hackathon
python main.py
```

### Continuous Monitoring
```bash
# Run every 5 minutes (default)
python main.py continuous

# Run every 10 minutes
python main.py continuous 10
```

### Using CrewAI CLI
```bash
# Run the crew
crewai run

# Train the crew
crewai train -n 5 -f training_data.pkl

# Test the crew
crewai test -n 3 -e gpt-4
```

## Configuration

### Miner Efficiency
Edit `MINER_WTH` in `proj/inputs.py`:
```python
MINER_WTH = 100  # Watts per TH/s (default: 100)
```

### Dashboard API
Update the endpoint in `main.py`:
```python
inputs = {
    'dashboard_api_endpoint': 'https://your-api.com/endpoint',
    'miner_efficiency': 100,
}
```

## Output

The crew generates:
- **mining_report.json**: Complete analysis with profit/carbon rankings
- **Console output**: Real-time insights and recommendations
- **Dashboard updates**: Via configured API endpoint

## Example Output

```
Region Rankings (Best Profit/Carbon Ratio):
--------------------------------------------------------------------------------
ISO      Avg LMP      Profit/TH/hr    Carbon       Profit/Carbon
         ($/MWh)      ($)             (gCO2/MWh)   ($/kgCO2)
--------------------------------------------------------------------------------
ISONE    $    -17.52  $      0.0082          350   $      0.0234
SPP      $     15.30  $      0.0049          450   $      0.0109
ERCOT    $     22.50  $      0.0041          520   $      0.0079
```

## Extending the System

### Adding New Tools
Create new tools in `tools/energy_tools.py`:
```python
class YourCustomTool(BaseTool):
    name: str = "Your Tool Name"
    description: str = "What it does"
    
    def _run(self):
        # Your logic here
        pass
```

### Adding New Agents
1. Define agent in `config/agents.yaml`
2. Create corresponding task in `config/tasks.yaml`
3. Add agent method in `crew.py`

## Environment Variables

```bash
# Optional: Set your GridStatus API key
export GRIDSTATUS_API_KEY="your-key-here"
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Market Intel   │────▶│  Environmental   │────▶│  Optimization   │
│     Agent       │     │     Analyst      │     │   Strategist    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         └───────────────────────┴─────────────────────────┘
                                 │
                                 ▼
                      ┌─────────────────────┐
                      │ Dashboard Publisher │
                      └─────────────────────┘
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Add your agents/tools
4. Submit a pull request

## License

MIT
