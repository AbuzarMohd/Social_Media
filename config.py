"""Centralized configuration & secret handling."""
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
        "REDDIT_CLIENT_ID": st.secrets.get("REDDIT_CLIENT_ID") or os.getenv("REDDIT_CLIENT_ID"),
        "REDDIT_CLIENT_SECRET": st.secrets.get("REDDIT_CLIENT_SECRET") or os.getenv("REDDIT_CLIENT_SECRET"),
        "REDDIT_USER_AGENT": st.secrets.get("REDDIT_USER_AGENT") or os.getenv("REDDIT_USER_AGENT"),
    }

    if not cfg["HF_TOKEN"]:
        raise RuntimeError("[config] Hugging Face API token not found in secrets or env.")

    if not cfg["REDDIT_CLIENT_ID"] or not cfg["REDDIT_CLIENT_SECRET"] or not cfg["REDDIT_USER_AGENT"]:
        raise RuntimeError("[config] Reddit API credentials not found.")

    return cfg
