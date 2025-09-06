"""
Live Mumbai Railway Simulation Launcher
Launches the real-time visualization with train movements
"""

import subprocess
import sys
import os
from pathlib import Path
import time
import webbrowser

def main():
    print("🚂 Mumbai Railway Live Simulation")
    print("=" * 50)
    print("Starting live visualization with real-time train movements...")
    
    # Get the correct Python executable
    project_root = Path(__file__).parent
    
    # Path to the live simulation script
    live_sim_path = project_root / "visualization" / "live_simulation.py"
    
    if not live_sim_path.exists():
        print(f"❌ Live simulation script not found at: {live_sim_path}")
        return
    
    try:
        # Get the Python executable path
        python_path = "C:/Users/Zaid/AppData/Local/Programs/Python/Python313/python.exe"
        
        print("\n🚀 Launching Streamlit dashboard...")
        print("📍 This will open in your web browser automatically")
        print("⏱️  Please wait while the server starts...")
        
        # Launch Streamlit
        cmd = [python_path, "-m", "streamlit", "run", str(live_sim_path)]
        
        # Run the command
        subprocess.run(cmd, cwd=str(project_root))
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Simulation stopped by user")
    except Exception as e:
        print(f"\n❌ Error launching live simulation: {e}")
        print("\nAlternative: Run manually with:")
        print(f"streamlit run {live_sim_path}")

if __name__ == "__main__":
    main()
