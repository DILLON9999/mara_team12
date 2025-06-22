#!/usr/bin/env python3
"""
Real-time Bitcoin Mining Optimization Dashboard
Visualizes agent workflows, data inputs, and optimization results
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import os
import sys
import threading
import time
from datetime import datetime, timedelta
import pandas as pd

# Add parent directory to path to import inputs module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from inputs import (
    get_cheapest_lmp, get_inference_competition_prices, get_btc_hashprice,
    get_carbon_intensity_by_iso, calculate_profit_per_carbon_intensity,
    calculate_hourly_mining_profit, MINER_WTH
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mara_hackathon_dashboard'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state for dashboard
dashboard_state = {
    'last_update': None,
    'agents_status': {
        'market_intelligence': {'status': 'idle', 'last_run': None, 'data': None},
        'environmental_analyst': {'status': 'idle', 'last_run': None, 'data': None},
        'hardware_scout': {'status': 'idle', 'last_run': None, 'data': None},
        'optimization_strategist': {'status': 'idle', 'last_run': None, 'data': None},
        'carbon_arbitrageur': {'status': 'idle', 'last_run': None, 'data': None},
        'dashboard_publisher': {'status': 'idle', 'last_run': None, 'data': None}
    },
    'live_data': {
        'lmp_data': None,
        'btc_data': None,
        'carbon_data': None,
        'profit_analysis': None,
        'inference_prices': None
    },
    'mining_report': None,
    'hardware_update': None,
    'current_miner_wth': MINER_WTH
}

def load_agent_outputs():
    """Load the latest agent outputs from JSON files"""
    try:
        # Load mining report
        if os.path.exists('mining_report.json'):
            with open('mining_report.json', 'r') as f:
                content = f.read().strip()
                if content and not content.startswith('{'):
                    # If it's plain text, wrap in a structure
                    dashboard_state['mining_report'] = {
                        'status': 'completed',
                        'message': content,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    dashboard_state['mining_report'] = json.loads(content) if content else None
        
        # Load hardware update
        if os.path.exists('hardware_update.json'):
            with open('hardware_update.json', 'r') as f:
                content = f.read().strip()
                if content:
                    hardware_data = json.loads(content)
                    dashboard_state['hardware_update'] = hardware_data
                    # Update current miner efficiency if recommended
                    if hardware_data.get('update') == 'yes' and 'MINER_WTH' in hardware_data:
                        dashboard_state['current_miner_wth'] = hardware_data['MINER_WTH']
                        
    except Exception as e:
        print(f"Error loading agent outputs: {e}")

def fetch_live_data():
    """Fetch live data from all sources"""
    try:
        # Update agent status
        dashboard_state['agents_status']['market_intelligence']['status'] = 'running'
        socketio.emit('agent_status_update', dashboard_state['agents_status'])
        
        # Fetch LMP data  
        print("Fetching LMP data...")
        lmp_data = get_cheapest_lmp(5)
        dashboard_state['live_data']['lmp_data'] = lmp_data
        dashboard_state['agents_status']['market_intelligence'] = {
            'status': 'completed',
            'last_run': datetime.now().isoformat(),
            'data': f"Fetched data from {len(lmp_data)} ISOs"
        }
        
        # Fetch BTC data
        print("Fetching BTC hashprice...")
        btc_data = get_btc_hashprice()
        dashboard_state['live_data']['btc_data'] = btc_data
        
        # Environmental analysis
        dashboard_state['agents_status']['environmental_analyst']['status'] = 'running'
        socketio.emit('agent_status_update', dashboard_state['agents_status'])
        
        print("Fetching carbon intensity...")
        carbon_data = get_carbon_intensity_by_iso()
        dashboard_state['live_data']['carbon_data'] = carbon_data
        dashboard_state['agents_status']['environmental_analyst'] = {
            'status': 'completed',
            'last_run': datetime.now().isoformat(),
            'data': f"Analyzed {len(carbon_data)} regions"
        }
        
        # Optimization analysis
        dashboard_state['agents_status']['optimization_strategist']['status'] = 'running'
        socketio.emit('agent_status_update', dashboard_state['agents_status'])
        
        print("Calculating profit optimization...")
        profit_analysis = calculate_profit_per_carbon_intensity(
            lmp_data, btc_data, carbon_data, dashboard_state['current_miner_wth']
        )
        dashboard_state['live_data']['profit_analysis'] = profit_analysis
        dashboard_state['agents_status']['optimization_strategist'] = {
            'status': 'completed',
            'last_run': datetime.now().isoformat(),
            'data': f"Optimized {len(profit_analysis)} mining locations"
        }
        
        # Inference prices
        print("Fetching inference competition prices...")
        inference_prices = get_inference_competition_prices()
        dashboard_state['live_data']['inference_prices'] = inference_prices
        
        dashboard_state['last_update'] = datetime.now().isoformat()
        
        # Load agent outputs
        load_agent_outputs()
        
        # Emit update to connected clients
        socketio.emit('data_update', dashboard_state)
        
        print(f"✅ Data update completed at {dashboard_state['last_update']}")
        
    except Exception as e:
        print(f"❌ Error fetching live data: {e}")
        # Update agent status to show error
        for agent in dashboard_state['agents_status']:
            if dashboard_state['agents_status'][agent]['status'] == 'running':
                dashboard_state['agents_status'][agent]['status'] = 'error'
                dashboard_state['agents_status'][agent]['data'] = str(e)

def background_data_fetcher():
    """Background thread to fetch data every 30 seconds"""
    while True:
        try:
            fetch_live_data()
            time.sleep(30)  # Update every 30 seconds
        except Exception as e:
            print(f"Background fetcher error: {e}")
            time.sleep(30)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    """API endpoint to get current data"""
    return jsonify(dashboard_state)

@app.route('/api/refresh')
def refresh_data():
    """Force refresh data"""
    fetch_live_data()
    return jsonify({'status': 'refreshed', 'timestamp': dashboard_state['last_update']})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('data_update', dashboard_state)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('request_refresh')
def handle_refresh_request():
    """Handle manual refresh request from client"""
    print('Manual refresh requested')
    fetch_live_data()

if __name__ == '__main__':
    # Initial data fetch
    print("🚀 Starting MARA Mining Optimization Dashboard")
    print("📊 Fetching initial data...")
    fetch_live_data()
    
    # Start background data fetcher
    data_thread = threading.Thread(target=background_data_fetcher, daemon=True)
    data_thread.start()
    
    print("🌐 Dashboard starting at http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 