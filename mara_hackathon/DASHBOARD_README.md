# ⚡ MARA Mining Optimization Dashboard

A real-time web dashboard for visualizing Bitcoin mining optimization across multiple dimensions: **profit**, **carbon intensity**, and **hardware efficiency**.

## 🚀 Quick Start

### Option 1: Easy Start (Recommended for Demo)
```bash
python start_dashboard.py
```

### Option 2: Manual Start
```bash
# Install dependencies
pip install -r dashboard_requirements.txt

# Run dashboard
python dashboard_app.py
```

### Option 3: Demo Mode (No APIs Required)
```bash
# Generate demo data first
python demo_data.py

# Then start dashboard
python start_dashboard.py
```

## 🌐 Access Dashboard

Once started, open your browser to:
**http://localhost:5000**

## 📊 Dashboard Features

### Real-Time Agent Workflow Visualization
- **6 Specialized Agents** with live status indicators
- **Workflow Pipeline**: Market Intelligence → Environmental Analysis → Hardware Scout → Optimization → Carbon Arbitrage → Dashboard Publishing
- **Color-coded Status**: 
  - 🟡 Running (with pulse animation)
  - 🟢 Completed
  - 🔴 Error
  - ⚫ Idle

### Live Data Visualizations
1. **Key Metrics Cards**
   - Current BTC Price
   - Hashprice ($/TH/day)
   - Miner Efficiency (W/TH)
   - Best Profit/Carbon Ratio

2. **Energy Price Chart**
   - Real-time LMP prices from all major ISOs
   - Bar chart showing $/MWh across regions

3. **Carbon Intensity Chart**
   - Environmental impact by power grid
   - gCO2/MWh measurements

4. **Profit Analysis Table**
   - Comprehensive mining profitability analysis
   - Profit per TH per hour
   - Profit per unit of carbon emissions
   - Profitability status indicators

### Hardware Update Alerts
- **Dynamic Hardware Recommendations**
- **Efficiency Improvement Notifications**
- **Automatic Miner W/TH Updates**

### Activity Log
- **Real-time System Activity**
- **Agent Execution Logs**
- **API Call Tracking**
- **Error Monitoring**

### Technical Details Panel
- **Agent Status Cards** with execution details
- **Latest Mining Reports**
- **System Performance Metrics**

## 🤖 Agent System Integration

The dashboard integrates with a 6-agent CrewAI system:

1. **Market Intelligence Agent**
   - Fetches LMP data from 8 major ISOs
   - Identifies cheapest energy locations
   - Tracks negative pricing opportunities

2. **Environmental Analyst**
   - Calculates carbon intensity by region
   - Monitors grid fuel mix changes
   - ESG compliance tracking

3. **Hardware Scout**
   - Scans for new ASIC hardware
   - Identifies efficiency improvements ≥5%
   - Updates system efficiency parameters

4. **Optimization Strategist**
   - Multi-dimensional optimization
   - Balances profit, carbon, and operations
   - Real-time decision making

5. **Carbon Arbitrageur**
   - Tracks carbon credit markets
   - Policy change monitoring
   - ESG opportunity identification

6. **Dashboard Publisher**
   - Formats insights for stakeholders
   - Real-time alert management
   - Executive summary generation

## 📈 Data Sources

### Live Data Mode
- **GridStatus.io**: Real-time LMP data from all ISOs
- **Mempool.space**: Bitcoin network statistics
- **GridStatus**: Fuel mix and carbon intensity
- **Market APIs**: Inference competition pricing

### Demo Mode
- **Realistic Sample Data**: For hackathon demonstrations
- **Dynamic Updates**: Simulated real-time changes
- **Full Feature Testing**: Without API dependencies

## 🔄 Auto-Refresh

- **Background Updates**: Every 30 seconds
- **Manual Refresh**: Click refresh button
- **WebSocket Communication**: Real-time updates
- **No Page Reload Required**

## 🛠️ Technical Architecture

### Backend (Flask + SocketIO)
- **Python Flask**: Web framework
- **WebSocket Support**: Real-time communication
- **Multi-threaded**: Background data fetching
- **API Integration**: Multiple data sources

### Frontend (Bootstrap + Chart.js)
- **Responsive Design**: Mobile-friendly
- **Interactive Charts**: Real-time updates
- **Modern UI**: Glassmorphism design
- **Real-time Updates**: Socket.IO client

### Data Pipeline
```
External APIs → Data Processing → Agent Analysis → Dashboard Updates → WebSocket → Frontend
```

## 📱 Mobile Responsive
- **Bootstrap 5**: Responsive grid system
- **Touch Friendly**: Mobile optimized
- **Adaptive Layout**: Works on all screen sizes

## 🎯 Perfect for Hackathon Demos

### Technical Audience Features
- **Live API Calls**: Real-time data fetching
- **Agent Workflow**: Visible processing pipeline
- **Error Handling**: Graceful degradation
- **Performance Metrics**: System monitoring
- **Code Integration**: Direct function calls

### Demo Mode Benefits
- **No API Keys Required**: Works offline
- **Instant Setup**: Ready in seconds
- **Realistic Data**: Market-accurate samples
- **Full Functionality**: All features available

## 🔧 Configuration

### Environment Variables (Optional)
```bash
FLASK_ENV=development
MINER_WTH=100  # Default miner efficiency
UPDATE_INTERVAL=30  # Seconds between updates
```

### Customization
- **Update Intervals**: Modify background refresh rate
- **Chart Colors**: Customize visualization themes
- **Data Sources**: Add new API endpoints
- **Agent Configuration**: Adjust workflow parameters

## 📊 Performance

- **Lightweight**: <2MB memory footprint
- **Fast Updates**: Sub-second refresh times
- **Scalable**: Handles multiple concurrent users
- **Efficient**: Minimal CPU usage

## 🔐 Security

- **CORS Enabled**: Cross-origin resource sharing
- **Input Validation**: Sanitized data processing
- **Error Handling**: Graceful failure modes
- **No Sensitive Data**: Public information only

## 🎨 UI/UX Design

- **Dark Theme**: Energy-focused aesthetic
- **Gold Accents**: Bitcoin-inspired colors
- **Smooth Animations**: Professional transitions
- **Clear Typography**: Easy to read metrics
- **Intuitive Layout**: Logical information hierarchy

## 📝 Usage Examples

### For Executives
- **High-level Metrics**: Key performance indicators
- **Profit Summaries**: Bottom-line impact
- **ESG Reporting**: Environmental compliance
- **Investment Decisions**: Hardware upgrade ROI

### For Operators
- **Real-time Monitoring**: System health
- **Regional Optimization**: Where to mine
- **Alert Management**: Critical notifications
- **Performance Tracking**: Efficiency metrics

### For Developers
- **API Integration**: Live data feeds
- **Agent Workflows**: Processing pipelines
- **Error Monitoring**: System diagnostics
- **Performance Metrics**: Resource usage

## 🔍 Troubleshooting

### Common Issues
1. **Port 5000 in use**: Change port in `dashboard_app.py`
2. **API timeouts**: System automatically falls back to demo data
3. **Missing dependencies**: Run `pip install -r dashboard_requirements.txt`
4. **WebSocket errors**: Check firewall settings

### Debug Mode
```bash
python dashboard_app.py --debug
```

## 🌟 Key Advantages

1. **Real-time Intelligence**: Live market data
2. **Multi-dimensional Optimization**: Profit + ESG
3. **Hardware Awareness**: Efficiency tracking
4. **Carbon Conscious**: Environmental impact
5. **Scalable Architecture**: Enterprise-ready
6. **Demo Ready**: Instant hackathon setup

---

**Perfect for demonstrating sophisticated Bitcoin mining optimization with real-time agent coordination and comprehensive business intelligence.** 