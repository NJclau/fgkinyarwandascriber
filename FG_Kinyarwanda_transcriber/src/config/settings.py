# src/config/settings.py

import streamlit as st
import os

class AppConfig:
    """Centralized configuration for the Streamlit application."""

    def __init__(self):
        # --- API Keys ---
        self.gemini_api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))

        # --- Admin Users ---
        self.admin_emails = st.secrets.get("ADMIN_EMAILS", [])

        # --- Authentication ---
        self.demo_mode = st.secrets.get("DEMO_MODE", True)
        self.allowed_emails = st.secrets.get("ALLOWED_EMAILS", [])

        # --- GPU Acceleration ---
        self.use_gpu = st.secrets.get("USE_GPU", False)

    def validate(self):
        """Validate that required secrets are present."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in secrets or environment variables.")
        if not self.admin_emails:
            st.warning("ADMIN_EMAILS is not configured in secrets.")

# Instantiate the config
config = AppConfig()

# You can optionally call validate() here to fail fast on startup
# try:
#     config.validate()
# except ValueError as e:
#     st.error(f"Configuration Error: {e}")
#     st.stop()
