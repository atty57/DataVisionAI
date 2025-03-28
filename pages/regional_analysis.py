import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.data_visualizer import create_choropleth_map, plot_regional_comparison

def app():
    st.title("Regional EV Adoption Analysis")
    
    # Check if data is loaded
    if 'cleaned_data' not in st.session_state or st.session_state.cleaned_data is None:
        st.warning("Please load data from the main page first.")
        return
    
    data = st.session_state.cleaned_data
    
    st.markdown("""
    This page provides a detailed comparison of EV adoption across different regions and countries,
    highlighting leaders and laggards in the electric vehicle transition.
    """)
    
    # Geographic visualization
    st.header("Geographic Distribution")
    
    # Year selector for map
    map_year = st.slider(
        "Select Year for Map",
        min_value=int(data['year'].min()),
        max_value=int(data['year'].max()),
        value=int(data['year'].max())
    )
    
    # Filter data for selected year
    year_data = data[data['year'] == map_year]
    
    # Metric selector for map
    map_metric = st.selectbox(
        "Select Metric for Map",
        options=['sales', 'market_share'] if 'market_share' in data.columns else ['sales'],
        index=0
    )
    
    # Create choropleth map
    map_fig = create_choropleth_map(
        year_data, 
        map_metric, 
        f'Global {map_metric.capitalize()} Distribution ({map_year})'
    )
    st.plotly_chart(map_fig, use_container_width=True)
    
    # Add map insights
    st.markdown("""
    **Map Insights:**
    - Darker colors indicate higher EV adoption in that region.
    - Geographic patterns often reflect policy environments and infrastructure availability.
    - Major automotive markets (China, Europe, North America) typically show higher adoption.
    """)
    
    # Regional comparison
    st.header("Regional Leaders and Laggards")
    
    # Year selector for comparison
    comp_year = st.slider(
        "Select Year for Comparison",
        min_value=int(data['year'].min()),
        max_value=int(data['year'].max()),
        value=int(data['year'].max()),
        key="comp_year_slider"
    )
    
    # Metric selector for comparison
    comp_metric = st.selectbox(
        "Select Metric for Comparison",
        options=['sales', 'market_share'] if 'market_share' in data.columns else ['sales'],
        index=0,
        key="comp_metric_selector"
    )
    
    # Create bar chart comparison
    comp_fig = plot_regional_comparison(
        data, 
        comp_year, 
        comp_metric
    )
    st.plotly_chart(comp_fig, use_container_width=True)
    
    # Regional trends over time
    st.header("Regional Trends Over Time")
    
    # Select regions to compare
    selected_regions = st.multiselect(
        "Select Regions to Compare",
        options=sorted(data['region'].unique()),
        default=sorted(data['region'].unique())[:5] if len(data['region'].unique()) > 5 else sorted(data['region'].unique())
    )
    
    if selected_regions:
        # Filter data for selected regions
        region_data = data[data['region'].isin(selected_regions)]
        
        # Group by region and year
        trend_data = region_data.groupby(['region', 'year'])['sales'].sum().reset_index()
        
        # Create line chart
        trend_fig = px.line(
            trend_data,
            x='year',
            y='sales',
            color='region',
            labels={'sales': 'EV Sales', 'year': 'Year', 'region': 'Region'},
            title='EV Sales Trends by Region'
        )
        
        trend_fig.update_layout(
            xaxis=dict(tickmode='linear'),
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(trend_fig, use_container_width=True)
        
        # Add trend insights
        st.markdown("""
        **Trend Insights:**
        - Compare the trajectories of different regions over time.
        - Note when certain regions began accelerating their EV adoption.
        - Look for parallel growth patterns or divergent trends.
        """)
        
        # Market share comparison if available
        if 'market_share' in data.columns:
            st.header("Market Share Comparison")
            
            # Group by region and year for market share
            market_data = region_data.groupby(['region', 'year'])['market_share'].mean().reset_index()
            
            # Create line chart for market share
            market_fig = px.line(
                market_data,
                x='year',
                y='market_share',
                color='region',
                labels={'market_share': 'Market Share (%)', 'year': 'Year', 'region': 'Region'},
                title='EV Market Share Trends by Region'
            )
            
            market_fig.update_layout(
                xaxis=dict(tickmode='linear'),
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(market_fig, use_container_width=True)
    else:
        st.info("Please select at least one region to visualize trends.")
    
    # Case studies
    st.header("Regional Case Studies")
    
    # Create tabs for different case studies
    tab1, tab2, tab3 = st.tabs(["Norway: EV Leader", "China: Largest Market", "US: Adoption Challenges"])
    
    with tab1:
        st.subheader("Norway: The Global EV Leader")
        st.markdown("""
        Norway has achieved the world's highest electric vehicle market share:
        
        - **Policy Support**: Tax exemptions and incentives for EV buyers
        - **Infrastructure**: Extensive charging network coverage
        - **Public Acceptance**: Strong cultural adoption of sustainable transport
        - **Results**: Over 80% of new car sales were electric in some months of 2021-2022
        
        Norway demonstrates how targeted policies can rapidly shift a market toward electrification.
        """)
    
    with tab2:
        st.subheader("China: The World's Largest EV Market")
        st.markdown("""
        China has established itself as the global leader in EV production and adoption:
        
        - **Government Push**: Strong central planning and industrial policy
        - **Domestic Industry**: Support for local manufacturers (BYD, NIO, etc.)
        - **Urban Focus**: Addressing air quality issues in megacities
        - **Results**: China accounts for over 50% of global EV sales
        
        China's approach highlights the role of industrial policy in accelerating the EV transition.
        """)
    
    with tab3:
        st.subheader("United States: Mixed Progress")
        st.markdown("""
        The US market shows regional variations in EV adoption:
        
        - **Policy Fragmentation**: Varying state-level approaches (California vs. other states)
        - **Infrastructure Challenges**: Charging network still developing
        - **Consumer Preferences**: Strong truck/SUV market presenting electrification challenges
        - **Recent Progress**: Major automotive investments and federal policy support
        
        The US case illustrates how geographic, cultural, and policy factors can create uneven adoption patterns.
        """)
