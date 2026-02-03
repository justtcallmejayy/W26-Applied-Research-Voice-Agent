

"""
src.app.dashboard.dashboard


"""

import streamlit as st
import logging

# Initialize logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
    handlers=[
        logging.FileHandler('src/app/logs/dashboard.log'),  # to file
        logging.StreamHandler()                     # to console
    ]
)


st.set_page_config(
    page_title="AI Voice Assistant",
    layout="wide"
)

st.title("AI Voice Assistant Dashboard")