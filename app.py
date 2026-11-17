"""
Hugging Face Spaces entry point for HealthLabelCheck.

HF Spaces with the Streamlit SDK looks for `app.py` at the repo root
and runs it directly with `streamlit run app.py`.

This file just re-exports the Streamlit app from app/streamlit_app.py
so the import paths stay consistent.
"""

# Standard library
import os
import sys

# Add repo root to path so `from app.xxx import ...` works
sys.path.insert(0, os.path.dirname(__file__))

# Import and run the full Streamlit UI
# (Streamlit executes all top-level code when it runs the file)
from app.streamlit_app import *  # noqa: F401, F403
