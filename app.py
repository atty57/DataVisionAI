import streamlit as st
import pandas as pd
import numpy as np
import os
from utils.data_loader import load_sample_data
from utils.data_processor import clean_data, calculate_growth_rates, calculate_market_share
from utils.data_visualizer import plot_global_trends, create_choropleth_map
from utils.forecasting import forecast_linear, forecast_polynomial, plot_forecast

# We're using Streamlit's built-in pages system with the numbered files in the pages directory
# No need to import pages explicitly

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
            data = pd.read_csv(uploaded_file)
            st.session_state.data = data
            with st.spinner("Cleaning and processing data..."):
                st.session_state.cleaned_data = clean_data(data)
                st.session_state.regions = st.session_state.cleaned_data['region'].unique().tolist()
                st.session_state.years = sorted(st.session_state.cleaned_data['year'].unique().tolist())
            st.sidebar.success("Data successfully loaded!")
        except Exception as e:
            st.sidebar.error(f"Error loading data: {e}")
            st.session_state.data = None
            st.session_state.cleaned_data = None
else:
    # Load sample data
    if st.session_state.data is None:
        with st.spinner("Loading sample data..."):
            st.session_state.data = load_sample_data()
            st.session_state.cleaned_data = clean_data(st.session_state.data)
            st.session_state.regions = st.session_state.cleaned_data['region'].unique().tolist()
            st.session_state.years = sorted(st.session_state.cleaned_data['year'].unique().tolist())
        st.sidebar.success("Sample data loaded!")

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
    
    # Filter data based on selections
    filtered_data = st.session_state.cleaned_data[
        (st.session_state.cleaned_data['year'] >= year_range[0]) &
        (st.session_state.cleaned_data['year'] <= year_range[1])
    ]
    
    if selected_regions:
        filtered_data = filtered_data[filtered_data['region'].isin(selected_regions)]
    
    # Calculate growth rates for filtered data
    growth_data = calculate_growth_rates(filtered_data)
    
    # Add some debugging information
    st.sidebar.header("Debug Info")
    if st.sidebar.checkbox("Show debug info"):
        st.sidebar.write(f"Data loaded: {st.session_state.data is not None}")
        st.sidebar.write(f"Cleaned data: {st.session_state.cleaned_data is not None}")
        if st.session_state.cleaned_data is not None:
            st.sidebar.write(f"Data shape: {st.session_state.cleaned_data.shape}")
            st.sidebar.write(f"Columns: {st.session_state.cleaned_data.columns.tolist()}")
    
    # Main page content - no need for navigation as Streamlit handles it automatically
    st.subheader("Dashboard Home")
    st.markdown("""
    This is the main dashboard page. Use the sidebar navigation to explore different analyses:
    
    - **Overview**: Get a global overview of electric vehicle adoption
    - **Regional Analysis**: Compare EV adoption across different regions
    - **Market Share**: Analyze how EVs are capturing market share from traditional vehicles
    - **Forecasting**: Predictive analytics for future EV adoption trends
    """)
    
    # Display some sample visualizations on the main page
    try:
        st.subheader("Global EV Adoption Trends")
        global_trend_fig = plot_global_trends(filtered_data, metric='sales', 
                                             title='Global EV Sales Over Time')
        st.plotly_chart(global_trend_fig, use_container_width=True)
        
        st.subheader("Geographic Distribution")
        latest_year = filtered_data['year'].max()
        latest_data = filtered_data[filtered_data['year'] == latest_year]
        map_fig = create_choropleth_map(latest_data, metric='sales', 
                                        title=f'EV Sales by Region ({latest_year})')
        st.plotly_chart(map_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error generating visualizations: {str(e)}")
        st.code(str(e), language="python")
else:
    st.info("Please load data to begin analysis.")

# Footer
st.markdown("---")
st.markdown("© 2023 Electric Vehicle Adoption Analysis Dashboard")
