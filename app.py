"""
Hugging Face Spaces entry point for HealthLabelCheck.

HF Spaces with the Streamlit SDK looks for `app.py` at the repo root
and runs it directly with `streamlit run app.py`.

This file re-exports the Streamlit UI from ui/app.py so the import
paths stay consistent with the Day 10 layout.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# Import and run the full Streamlit UI
from ui.app import *  # noqa: F401, F403
