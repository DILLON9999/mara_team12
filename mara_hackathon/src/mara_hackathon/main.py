#!/usr/bin/env python
import sys
import warnings
import time
from datetime import datetime

from mara_hackathon.crew import MaraHackathon

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'dashboard_api_endpoint': 'https://api.example.com/mining-dashboard',  # Replace with actual endpoint
        'miner_efficiency': 100,  # Watts per TH/s
        'current_timestamp': datetime.now().isoformat()
    }
    
    try:
        print("🚀 Starting Energy-Bitcoin Mining Optimization Crew...")
        print(f"⏰ Current time: {inputs['current_timestamp']}")
        print("-" * 50)
        
        result = MaraHackathon().crew().kickoff(inputs=inputs)
        
        print("\n✅ Crew execution completed!")
        print("-" * 50)
        
        return result
        
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def run_continuous(interval_minutes=5):
    """
    Run the crew continuously at specified intervals.
    """
    print(f"🔄 Starting continuous monitoring (every {interval_minutes} minutes)")
    
    while True:
        try:
            print(f"\n{'='*60}")
            print(f"🔄 Running analysis at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}\n")
            
            run()
            
            print(f"\n⏳ Waiting {interval_minutes} minutes until next run...")
            time.sleep(interval_minutes * 60)
            
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Error occurred: {e}")
            print(f"⏳ Retrying in {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'dashboard_api_endpoint': 'https://api.example.com/mining-dashboard',
        'miner_efficiency': 100,
        'current_timestamp': datetime.now().isoformat()
    }
    try:
        MaraHackathon().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        MaraHackathon().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'dashboard_api_endpoint': 'https://api.example.com/mining-dashboard',
        'miner_efficiency': 100,
        'current_timestamp': datetime.now().isoformat()
    }
    
    try:
        MaraHackathon().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


if __name__ == "__main__":
    # Allow running with 'continuous' argument for continuous monitoring
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        run_continuous(interval)
    else:
        run()
