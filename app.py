import streamlit as st
import pandas as pd
import numpy as np
import os
from utils.data_loader import load_sample_data
from utils.data_processor import clean_data, calculate_growth_rates
from utils.data_visualizer import plot_global_trends, create_choropleth_map

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
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=min(st.session_state.years),
        max_value=max(st.session_state.years),
        value=(min(st.session_state.years), max(st.session_state.years))
    )
    
    # Region selector
    selected_regions = st.sidebar.multiselect(
        "Select Regions",
        options=st.session_state.regions,
        default=st.session_state.regions[:5] if len(st.session_state.regions) > 5 else st.session_state.regions
    )
    
    # Filter data based on selections
    filtered_data = st.session_state.cleaned_data[
        (st.session_state.cleaned_data['year'] >= year_range[0]) &
        (st.session_state.cleaned_data['year'] <= year_range[1])
    ]
    
    if selected_regions:
        filtered_data = filtered_data[filtered_data['region'].isin(selected_regions)]
    
    # Calculate growth rates for filtered data
    growth_data = calculate_growth_rates(filtered_data)
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["Global Trends", "Regional Comparison", "Market Analysis"])
    
    with tab1:
        st.header("Global EV Adoption Trends")
        st.markdown("This section shows the overall trend of electric vehicle adoption globally.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("EV Sales Over Time")
            fig = plot_global_trends(filtered_data, 'sales', 'Total EV Sales by Year')
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Year-over-Year Growth Rates")
            if not growth_data.empty:
                # Filter growth rates to remove extreme outliers
                valid_growth = growth_data[growth_data['growth_rate'].between(-100, 200)]
                if not valid_growth.empty:
                    import plotly.express as px
                    fig = px.line(
                        valid_growth, x='year', y='growth_rate', color='region',
                        labels={'growth_rate': 'YoY Growth Rate (%)', 'year': 'Year', 'region': 'Region'},
                        title='Year-over-Year Growth in EV Sales'
                    )
                    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data to calculate meaningful growth rates.")
            else:
                st.info("Not enough data to calculate growth rates.")
    
    with tab2:
        st.header("Regional Comparison")
        st.markdown("Compare EV adoption across different regions and countries.")
        
        # Choropleth map
        st.subheader("EV Adoption by Region")
        latest_year = filtered_data['year'].max()
        latest_data = filtered_data[filtered_data['year'] == latest_year]
        
        if not latest_data.empty:
            fig = create_choropleth_map(latest_data, 'sales', f'EV Sales by Region ({latest_year})')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No data available for the selected year {latest_year}.")
            
        # Bar chart comparing regions
        st.subheader("Regional Leaders and Laggards")
        import plotly.express as px
        
        # Aggregate data by region for the latest year
        region_summary = latest_data.groupby('region')['sales'].sum().reset_index()
        region_summary = region_summary.sort_values('sales', ascending=False)
        
        fig = px.bar(
            region_summary, x='region', y='sales',
            labels={'sales': 'Total EV Sales', 'region': 'Region'},
            title=f'EV Sales by Region in {latest_year}',
            color='sales',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("Market Share Analysis")
        st.markdown("Analyze EV market share and composition over time.")
        
        if 'market_share' in filtered_data.columns:
            # Line chart of market share evolution
            st.subheader("EV Market Share Evolution")
            market_data = filtered_data.groupby(['year', 'region'])['market_share'].mean().reset_index()
            
            fig = px.line(
                market_data, x='year', y='market_share', color='region',
                labels={'market_share': 'EV Market Share (%)', 'year': 'Year', 'region': 'Region'},
                title='Evolution of EV Market Share by Region'
            )
            fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig, use_container_width=True)
            
            # Market share heatmap
            st.subheader("Market Share Comparison")
            pivot_data = market_data.pivot(index='region', columns='year', values='market_share').fillna(0)
            
            import plotly.figure_factory as ff
            if not pivot_data.empty:
                fig = ff.create_annotated_heatmap(
                    z=pivot_data.values,
                    x=list(map(str, pivot_data.columns.tolist())),
                    y=pivot_data.index.tolist(),
                    annotation_text=np.around(pivot_data.values, 1),
                    colorscale='Viridis',
                    showscale=True
                )
                fig.update_layout(
                    title='EV Market Share by Region and Year (%)',
                    xaxis_title='Year',
                    yaxis_title='Region'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough market share data available for the selected filters.")
        else:
            st.info("Market share data is not available in the current dataset.")
else:
    st.info("Please load data to begin analysis.")

# Footer
st.markdown("---")
st.markdown("© 2023 Electric Vehicle Adoption Analysis Dashboard")
