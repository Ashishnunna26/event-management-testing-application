# Root entry point for Streamlit Community Cloud.
# Streamlit Cloud looks for streamlit_app.py at the repo root by default.
# This simply re-executes the real app so all relative paths stay consistent.
import runpy, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
runpy.run_path(os.path.join(ROOT, "frontend", "app.py"), run_name="__main__")
