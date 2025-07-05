from config import get_settings
from backend.utils import log

THRESHOLD = 60  # send alert if score >=


def _twilio_client():
    cfg = get_settings()
    try:
        from twilio.rest import Client
    except ImportError:
        log("twilio not installed – alerts disabled.")
        return None
    if not (cfg["TWILIO_SID"] and cfg["TWILIO_AUTH"]):
        log("Twilio secrets missing.")
        return None
    return Client(cfg["TWILIO_SID"], cfg["TWILIO_AUTH"])


def maybe_send_alert(risk_score, df):
    if risk_score < THRESHOLD:
        return
    client = _twilio_client()
    if not client:
        return
    cfg = get_settings()
    body = f"⚠️ Mental‑health risk score is {risk_score:.1f}. Recent post: '{df.iloc[-1]['text'][:120]}…'"
    try:
        client.messages.create(to=cfg["ALERT_PHONE"], from_="+15005550006", body=body)
        log("Alert sent.")
    except Exception as e:
        log(f"Alert failed: {e}")