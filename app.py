import streamlit as st
import pandas as pd
import numpy as np
import os
from utils.data_loader import load_sample_data, load_data_from_csv, get_data_metadata, load_filtered_data
from utils.data_processor import clean_data, calculate_growth_rates, calculate_market_share
from utils.data_visualizer import plot_global_trends, create_choropleth_map
from utils.forecasting import forecast_linear, forecast_polynomial, plot_forecast

# Import page functions from the consolidated dashboard_pages.py file
from dashboard_pages import overview_page, regional_analysis_page, market_share_page, forecasting_page

# Set page configuration
st.set_page_config(
    page_title="Electric Vehicle Adoption Analysis",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state for data
if 'data' not in st.session_state:
    st.session_state.data = None
    st.session_state.cleaned_data = None
    st.session_state.regions = None
    st.session_state.years = None

# Title and introduction
st.title("Electric Vehicle Adoption Analysis Dashboard")

st.markdown("""
This interactive dashboard analyzes global Electric Vehicle (EV) adoption trends over time.
Explore data on EV sales, market share, regional comparisons, and future forecasts.

Electric vehicles have rapidly transitioned from a niche to a mainstream transport option in the past decade,
with urgent need to decarbonize transportation - a sector responsible for roughly one-fifth of global CO₂ emissions.
""")

# Sidebar for data loading and filtering
st.sidebar.header("Data Controls")

# Data loading options
data_source = st.sidebar.radio(
    "Choose data source",
    ["Use sample data", "Upload your own CSV"]
)

if data_source == "Upload your own CSV":
    uploaded_file = st.sidebar.file_uploader("Upload EV data CSV", type=['csv'])
    if uploaded_file is not None:
        try:
            # Save the uploaded file temporarily
            temp_file_path = f"temp_upload_{uploaded_file.name}"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Load data from CSV into database
            with st.spinner("Loading and processing CSV data..."):
                data = load_data_from_csv(temp_file_path)
                st.session_state.data = data
                st.session_state.cleaned_data = clean_data(data)
                
                # Get metadata from database
                st.session_state.regions, st.session_state.years = get_data_metadata()
                
            # Remove temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
            st.sidebar.success("Data successfully loaded and stored in database!")
        except Exception as e:
            st.sidebar.error(f"Error loading data: {e}")
            st.session_state.data = None
            st.session_state.cleaned_data = None
else:
    # Load sample data
    if st.session_state.data is None:
        with st.spinner("Loading sample data..."):
            # Initialize database and load sample data
            from utils.database import init_db
            try:
                # Initialize database
                init_db()
                
                # Load sample data (will create if not exists)
                st.session_state.data = load_sample_data()
                st.session_state.cleaned_data = clean_data(st.session_state.data)
                
                # Get metadata from database
                st.session_state.regions, st.session_state.years = get_data_metadata()
                
                if not st.session_state.regions or not st.session_state.years:
                    # Fallback if metadata wasn't retrieved correctly
                    st.session_state.regions = st.session_state.cleaned_data['region'].unique().tolist()
                    st.session_state.years = sorted(st.session_state.cleaned_data['year'].unique().tolist())
                    
                st.sidebar.success("Sample data loaded!")
            except Exception as e:
                st.sidebar.error(f"Error loading sample data: {e}")
                st.session_state.data = None
                st.session_state.cleaned_data = None

# Data filtering options (only if data is loaded)
if st.session_state.cleaned_data is not None:
    st.sidebar.header("Filters")
    
    # Year range selector
    if st.session_state.years:
        min_year = min(st.session_state.years)
        max_year = max(st.session_state.years)
        year_range = st.sidebar.slider(
            "Select Year Range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year)
        )
    else:
        year_range = (2010, 2023)  # Default range if years not available
    
    # Region selector
    if st.session_state.regions:
        default_regions = st.session_state.regions[:5] if len(st.session_state.regions) > 5 else st.session_state.regions
        selected_regions = st.sidebar.multiselect(
            "Select Regions",
            options=st.session_state.regions,
            default=default_regions
        )
    else:
        selected_regions = []  # Default empty selection if regions not available
    
    # Load filtered data directly from database
    with st.spinner("Loading filtered data from database..."):
        filtered_data = load_filtered_data(
            min_year=year_range[0],
            max_year=year_range[1],
            regions=selected_regions if selected_regions else None
        )
    
    # Calculate growth rates for filtered data
    growth_data = calculate_growth_rates(filtered_data)
    
    # Navigation between pages
    st.sidebar.header("Navigation")
    page = st.sidebar.radio(
        "Go to Page",
        ["Overview", "Regional Analysis", "Market Share", "Forecasting"],
        index=0
    )
    
    # Add some debugging information
    st.sidebar.header("Debug Info")
    if st.sidebar.checkbox("Show debug info"):
        st.sidebar.write(f"Current page: {page}")
        st.sidebar.write(f"Data loaded: {st.session_state.data is not None}")
        st.sidebar.write(f"Cleaned data: {st.session_state.cleaned_data is not None}")
        if st.session_state.cleaned_data is not None:
            st.sidebar.write(f"Data shape: {st.session_state.cleaned_data.shape}")
            st.sidebar.write(f"Columns: {st.session_state.cleaned_data.columns.tolist()}")
    
    # Display the selected page
    try:
        if page == "Overview":
            overview_page()
        elif page == "Regional Analysis":
            regional_analysis_page()
        elif page == "Market Share":
            market_share_page()
        elif page == "Forecasting":
            forecasting_page()
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        st.code(str(e), language="python")
else:
    st.info("Please load data to begin analysis.")

# Footer
st.markdown("---")
st.markdown("© 2023 Electric Vehicle Adoption Analysis Dashboard")
