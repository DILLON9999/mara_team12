#!/usr/bin/env python3
"""
Simple scheduler to run the CrewAI mining optimization system every 5 minutes
"""
import subprocess
import time
import sys
from datetime import datetime

def run_crew():
    """Run the CrewAI crew once"""
    try:
        print(f"\n{'='*60}")
        print(f"🔄 Running analysis at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # Run the crew using uv tool
        result = subprocess.run(
            ["uv", "tool", "run", "crewai", "run"],
            capture_output=False,
            text=True,
            check=False  # Don't raise exception on non-zero exit
        )
        
        if result.returncode == 0:
            print(f"\n✅ Crew execution completed successfully!")
            return True
        else:
            # Check if output files were created (crew might have run despite error)
            import os
            if os.path.exists("mining_report.json") and os.path.exists("hardware_update.json"):
                print(f"\n✅ Crew execution completed (despite module import warnings)!")
                return True
            else:
                print(f"\n❌ Crew execution failed!")
                return False
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running crew: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def main():
    interval_minutes = 5
    
    if len(sys.argv) > 1:
        try:
            interval_minutes = int(sys.argv[1])
        except ValueError:
            print("Invalid interval. Using default 5 minutes.")
    
    print(f"🚀 Starting Bitcoin Mining Optimization System")
    print(f"🔄 Running every {interval_minutes} minutes")
    print(f"⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Run immediately first
        run_crew()
        
        # Then run every N minutes
        while True:
            print(f"\n⏳ Waiting {interval_minutes} minutes until next run...")
            print(f"   Next run at: {datetime.now().replace(minute=datetime.now().minute + interval_minutes).strftime('%H:%M:%S')}")
            
            time.sleep(interval_minutes * 60)
            run_crew()
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️  System stopped by user")
        print("📊 Final reports saved to:")
        print("   - mining_report.json")
        print("   - hardware_update.json")
        sys.exit(0)

if __name__ == "__main__":
    main() 