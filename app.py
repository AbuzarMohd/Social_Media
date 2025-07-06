'''
import streamlit as st
import pandas as pd
from backend.collector import get_recent_posts
from backend.preprocess import preprocess_texts
from backend.emotion_model import analyse_batch
from backend.risk import compute_risk_score
from backend.alert import maybe_send_alert
from dashboard.charts import emotion_timeline_chart
from dashboard.components import sidebar_controls, header

st.set_page_config(page_title="Mental Health Monitor", layout="wide")

header()

# Sidebar inputs
username, platform, max_items, alert_on = sidebar_controls()

if st.button("Analyse"):  # main action
    with st.spinner("Fetching posts …"):
        raw_posts = get_recent_posts(username=username, platform=platform, limit=max_items)

    if not raw_posts:
        st.warning("No posts fetched; check username/API quota.")
        st.stop()

    with st.spinner("Pre‑processing & classifying …"):
        cleaned = preprocess_texts([p["text"] for p in raw_posts])
        df = analyse_batch(cleaned)

    # Combine with metadata
    meta_df = pd.DataFrame(raw_posts)
    full_df = pd.concat([meta_df, df], axis=1)

    # Risk scoring
    risk = compute_risk_score(full_df)
    st.metric("Current Risk Score", f"{risk:.1f}", delta=None)

    # Chart
    fig = emotion_timeline_chart(full_df)
    st.plotly_chart(fig, use_container_width=True)

    # Alerting
    if alert_on:
        maybe_send_alert(risk, full_df)

    # Raw table expander
    with st.expander("Raw predictions"):
        st.dataframe(full_df, use_container_width=True)

'''

import streamlit as st
import pandas as pd

from backend.collector import get_recent_posts
from backend.preprocess import preprocess_texts
from backend.emotion_model import analyse_batch
from backend.risk import compute_risk_score
from backend.alert import maybe_send_alert
from dashboard.charts import emotion_timeline_chart
from dashboard.components import sidebar_controls, header

st.set_page_config(page_title="Mental Health Monitor", layout="wide")

header()

# Sidebar controls
username, platform, max_items, alert_on = sidebar_controls()

if st.button("Analyse"):
    with st.spinner("Fetching posts …"):
        raw_posts = get_recent_posts(username=username, platform=platform, limit=max_items)

    if not raw_posts:
        st.warning("No posts fetched; check username or API access.")
        st.stop()

    with st.spinner("Pre-processing & classifying …"):
        cleaned = preprocess_texts([p["text"] for p in raw_posts])
        df = analyse_batch(cleaned)

    # Combine model output with metadata
    meta_df = pd.DataFrame(raw_posts)
    full_df = pd.concat([meta_df, df], axis=1)

    # Risk score
    risk = compute_risk_score(full_df)
    st.metric("Current Risk Score", f"{risk:.1f}")

    # Chart
    fig = emotion_timeline_chart(full_df)
    st.plotly_chart(fig, use_container_width=True)

    # Alert
    if alert_on:
        maybe_send_alert(risk, full_df)

    # Optional data preview
    with st.expander("🧾 Raw predictions"):
        st.dataframe(full_df, use_container_width=True)
