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
        # Create main area for upload status and animations
        upload_placeholder = st.empty()
        
        with upload_placeholder.container():
            # Create progress tracking elements
            st.markdown("### 📊 Processing Uploaded Data")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Save uploaded file temporarily
                status_text.info("⏳ Receiving uploaded file...")
                temp_file_path = f"temp_upload_{uploaded_file.name}"
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                progress_bar.progress(20)
                
                # Step 2: Validate CSV format
                status_text.info("⏳ Validating CSV format...")
                import pandas as pd
                file_preview = pd.read_csv(temp_file_path, nrows=5)
                progress_bar.progress(40)
                
                # Show preview of the data
                st.markdown("#### File Preview:")
                st.dataframe(file_preview, use_container_width=True)
                
                # Step 3: Load into database
                status_text.info("⏳ Loading data into database...")
                data = load_data_from_csv(temp_file_path)
                st.session_state.data = data
                progress_bar.progress(60)
                
                # Step 4: Clean and process data
                status_text.info("⏳ Processing and organizing data...")
                st.session_state.cleaned_data = clean_data(data)
                progress_bar.progress(80)
                
                # Step 5: Extract metadata
                status_text.info("⏳ Finalizing data setup...")
                st.session_state.regions, st.session_state.years = get_data_metadata()
                progress_bar.progress(100)
                
                # Show success message and data summary
                status_text.success(f"✅ Data successfully loaded and stored in database!")
                
                # Display data summary
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Records", f"{len(data):,}")
                col2.metric("Regions", f"{len(st.session_state.regions)}")
                col3.metric("Time Period", f"{min(st.session_state.years)} - {max(st.session_state.years)}")
                
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                
                # Show success in sidebar
                st.sidebar.success("✅ CSV data successfully loaded!")
                
                # Wait a moment to show completion
                import time
                time.sleep(2)
                upload_placeholder.empty()
                
            except Exception as e:
                # Show error message
                progress_bar.progress(100)
                status_text.error(f"❌ Error: {str(e)}")
                st.sidebar.error(f"Error loading data: {e}")
                
                # Clean up if needed
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                
                # Reset session state
                st.session_state.data = None
                st.session_state.cleaned_data = None
                
                # Wait a moment to show the error
                import time
                time.sleep(3)
                upload_placeholder.empty()
else:
    # Load sample data
    if st.session_state.data is None:
        # Create main loading animation containers
        loading_placeholder = st.empty()
        with loading_placeholder.container():
            # Create a progress bar for visual feedback
            st.markdown("### 🚀 Initializing EV Adoption Dashboard")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Initialize database and load sample data
            from utils.database import init_db
            try:
                # Step 1: Initialize database
                status_text.info("⏳ Setting up database...")
                init_db()
                progress_bar.progress(25)
                
                # Step 2: Check for existing data or generate sample data
                status_text.info("⏳ Preparing EV adoption data...")
                st.session_state.data = load_sample_data()
                progress_bar.progress(50)
                
                # Step 3: Process and clean data
                status_text.info("⏳ Processing and analyzing data...")
                st.session_state.cleaned_data = clean_data(st.session_state.data)
                progress_bar.progress(75)
                
                # Step 4: Extract metadata
                status_text.info("⏳ Extracting metadata and preparing visualizations...")
                st.session_state.regions, st.session_state.years = get_data_metadata()
                
                if not st.session_state.regions or not st.session_state.years:
                    # Fallback if metadata wasn't retrieved correctly
                    st.session_state.regions = st.session_state.cleaned_data['region'].unique().tolist()
                    st.session_state.years = sorted(st.session_state.cleaned_data['year'].unique().tolist())
                
                # Complete the loading process
                progress_bar.progress(100)
                status_text.success(f"✅ Dashboard ready! Loaded data for {len(st.session_state.regions)} regions from {min(st.session_state.years)} to {max(st.session_state.years)}")
                
                # Add quick stats
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Records", f"{len(st.session_state.data):,}")
                col2.metric("Regions", f"{len(st.session_state.regions)}")
                col3.metric("Time Period", f"{min(st.session_state.years)} - {max(st.session_state.years)}")
                
                # Add a small delay for user to see the completion
                import time
                time.sleep(1.5)
                
                # Remove the loading animation after completion
                loading_placeholder.empty()
                
                # Show success message in sidebar
                st.sidebar.success("✅ Sample data loaded successfully!")
                
            except Exception as e:
                # Show error in loading container and sidebar
                status_text.error(f"❌ Error: {str(e)}")
                st.sidebar.error(f"Error loading sample data: {e}")
                st.session_state.data = None
                st.session_state.cleaned_data = None
                
                # Wait a moment to show the error
                import time
                time.sleep(2)
                loading_placeholder.empty()

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
        # Add loading animation container
        loading_container = st.empty()
        loading_container.info("⏳ Fetching data from database...")
        
        # Load data with progress indication
        filtered_data = load_filtered_data(
            min_year=year_range[0],
            max_year=year_range[1],
            regions=selected_regions if selected_regions else None
        )
        
        # Clear loading message and display success
        loading_container.empty()
        if not filtered_data.empty:
            loading_container.success(f"✅ Data loaded successfully! ({len(filtered_data)} records)")
        else:
            loading_container.warning("⚠️ No data found for selected filters.")
    
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
st.markdown("© 2023 Your Name")
