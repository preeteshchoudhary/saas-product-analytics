import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    # Streamlit Cloud deployment path handling
    base_path = "data" if os.path.exists("data") else "../data"
    
    users = pd.read_csv(f"{base_path}/users.csv")
    events = pd.read_csv(f"{base_path}/events.csv")
    sessions = pd.read_csv(f"{base_path}/sessions.csv")
    subs = pd.read_csv(f"{base_path}/subscriptions.csv")
    ab_tests = pd.read_csv(f"{base_path}/ab_tests.csv")
    
    # Convert dates
    users['signup_date'] = pd.to_datetime(users['signup_date'])
    sessions['start_time'] = pd.to_datetime(sessions['start_time'])
    
    return users, events, sessions, subs, ab_tests