import subprocess
import sys

subprocess.run([
    sys.executable, "-m", "uvicorn",
    "backend.main:app",
    "--reload",
    "--port", "8000"
])
