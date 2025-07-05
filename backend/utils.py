import streamlit as st, datetime as dt

def log(msg):
    st.write(f"[{dt.datetime.now().isoformat(timespec='seconds')}] {msg}")