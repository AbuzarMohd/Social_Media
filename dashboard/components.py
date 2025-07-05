import streamlit as st

def header():
    st.title("🧠 Social Media Mental‑Health Monitor")
    st.write("Track emotional well‑being signals from Twitter / Reddit posts in real time.")


def sidebar_controls():
    st.sidebar.header("Configuration")
    platform = st.sidebar.selectbox("Platform", ["Twitter", "Reddit"])
    username = st.sidebar.text_input("Username", placeholder="jack")
    max_items = st.sidebar.slider("Posts to fetch", 10, 200, 50)
    alert_on = st.sidebar.checkbox("Enable SMS alerts", value=False)
    return username, platform, max_items, alert_on