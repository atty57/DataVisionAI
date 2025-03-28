
import streamlit as st
from pages.forecasting import app

st.set_page_config(
    page_title="EV Adoption Forecasting",
    page_icon="📈",
    layout="wide"
)

app()
