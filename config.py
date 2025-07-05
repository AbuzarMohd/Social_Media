"""Centralised configuration & secret handling."""
from functools import lru_cache
import os
import streamlit as st

@lru_cache(maxsize=1)
def get_settings():
    cfg = {
        "HF_TOKEN": st.secrets.get("HF_API_TOKEN") or os.getenv("HF_API_TOKEN"),
        "TWITTER_BEARER": st.secrets.get("TWITTER_BEARER_TOKEN"),
        "TWILIO_SID": st.secrets.get("TWILIO_SID"),
        "TWILIO_AUTH": st.secrets.get("TWILIO_AUTH"),
        "ALERT_PHONE": st.secrets.get("ALERT_PHONE"),
    }
    if not cfg["HF_TOKEN"]:
        raise RuntimeError("[config] Hugging Face API token not found in secrets or env.")
    return cfg