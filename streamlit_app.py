# streamlit_app.py
import streamlit as st
from app import home, dashboard

# Initialize session state if not already set
if 'page' not in st.session_state:
    st.session_state.page = "home"

# Routing logic
if st.session_state.page == "home":
    home.show()
elif st.session_state.page == "dashboard":
    dashboard.show()
