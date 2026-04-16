import subprocess
import sys

subprocess.run([
    sys.executable, "-m", "streamlit",
    "run", "frontend/app.py",
    "--server.port", "8501"
])
