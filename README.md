# Social Media Mental Health Monitor

Streamlit dashboard that monitors public Twitter/Reddit posts, classifies emotion & sentiment, computes a mental‑health risk score, and optionally sends alerts.

## Quick Start
1. **Clone** the repo and `cd` in.  
2. Create a virtualenv (optional) and `pip install -r requirements.txt`.  
3. Add a `.streamlit/secrets.toml` file **or** set env vars locally:

```toml
HF_API_TOKEN = "hf_..."
TWITTER_BEARER_TOKEN = "..."      # optional – else uses demo data
TWILIO_SID = "..."                # optional
TWILIO_AUTH = "..."
ALERT_PHONE = "+911234567890"      # who receives SMS