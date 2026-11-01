# run.py
# Entry point to run the Streamlit application
# Usage: python run.py

import subprocess
import sys
import os

if __name__ == "__main__":
    # Run the Streamlit application
    app_path = os.path.join(os.path.dirname(__file__), "app", "main.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
