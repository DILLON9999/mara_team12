#!/usr/bin/env python3
"""
Startup script for the MARA Mining Optimization Dashboard
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    try:
        print("Installing dashboard requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "dashboard_requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True

def main():
    print("🚀 Starting MARA Mining Optimization Dashboard")
    print("=" * 50)
    
    # Check if requirements are installed
    try:
        import flask
        import flask_socketio
        print("✅ Dependencies already installed")
    except ImportError:
        print("📦 Installing dependencies...")
        if not install_requirements():
            sys.exit(1)
    
    # Start the dashboard
    print("🌐 Starting dashboard server...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        from dashboard_app import app, socketio
        socketio.run(app, debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n⏹️  Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 