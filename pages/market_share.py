import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
from utils.data_visualizer import plot_market_share_evolution, create_stacked_area_chart

def app():
    st.title("EV Market Share Analysis")
    
    # Check if data is loaded
    if 'cleaned_data' not in st.session_state or st.session_state.cleaned_data is None:
        st.warning("Please load data from the main page first.")
        return
    
    data = st.session_state.cleaned_data
    
    st.markdown("""
    This page analyzes the market penetration of electric vehicles over time,
    examining what percentage of new vehicle sales are electric and how this varies by region.
    """)
    
    # Check if market share data is available
    has_market_share = 'market_share' in data.columns
    has_vehicle_type = 'vehicle_type' in data.columns
    
    if has_market_share:
        # Market share evolution
        st.header("EV Market Share Evolution")
        
        market_fig = plot_market_share_evolution(data)
        st.plotly_chart(market_fig, use_container_width=True)
        
        # Add market share insights
        st.markdown("""
        **Market Share Insights:**
        - Market share represents the percentage of new vehicle sales that are electric.
        - It's a key indicator of EV adoption relative to the overall vehicle market.
        - Some regions have achieved significant market share milestones (e.g., Norway >80%).
        """)
        
        # Market share comparison by region for latest year
        st.header("Market Share Comparison by Region")
        
        latest_year = data['year'].max()
        latest_data = data[data['year'] == latest_year]
        
        # Group by region and calculate average market share
        region_market = latest_data.groupby('region')['market_share'].mean().reset_index()
        region_market = region_market.sort_values('market_share', ascending=False)
        
        # Create bar chart
        market_bar_fig = px.bar(
            region_market,
            x='region',
            y='market_share',
            color='market_share',
            labels={'market_share': 'Market Share (%)', 'region': 'Region'},
            title=f'EV Market Share by Region in {latest_year}',
            color_continuous_scale='Viridis'
        )
        
        market_bar_fig.update_layout(
            xaxis={'categoryorder': 'total descending'},
            hovermode='closest'
        )
        
        st.plotly_chart(market_bar_fig, use_container_width=True)
        
        # Market share heatmap over time
        st.header("Market Share Evolution Heatmap")
        
        # Select regions for heatmap
        heatmap_regions = st.multiselect(
            "Select Regions for Heatmap",
            options=sorted(data['region'].unique()),
            default=sorted(data['region'].unique())[:10] if len(data['region'].unique()) > 10 else sorted(data['region'].unique())
        )
        
        if heatmap_regions:
            # Filter data for selected regions
            heatmap_data = data[data['region'].isin(heatmap_regions)]
            
            # Group by region and year, calculate mean market share
            pivot_data = heatmap_data.groupby(['region', 'year'])['market_share'].mean().reset_index()
            
            # Create pivot table
            pivot_table = pivot_data.pivot(index='region', columns='year', values='market_share').fillna(0)
            
            # Create heatmap
            if not pivot_table.empty:
                fig = ff.create_annotated_heatmap(
                    z=pivot_table.values,
                    x=list(map(str, pivot_table.columns.tolist())),
                    y=pivot_table.index.tolist(),
                    annotation_text=np.around(pivot_table.values, 1),
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
                st.info("Not enough data to create a meaningful heatmap.")
        else:
            st.info("Please select at least one region for the heatmap visualization.")
    
    else:
        st.warning("Market share data is not available in the current dataset. Only sales data will be displayed.")
    
    # EV composition analysis
    if has_vehicle_type:
        st.header("EV Composition Analysis")
        
        st.markdown("""
        This section shows the breakdown of EV sales by vehicle type (e.g., BEV vs. PHEV, or by vehicle category).
        """)
        
        # Create stacked area chart for vehicle composition
        composition_fig = create_stacked_area_chart(
            data,
            'vehicle_type',
            'sales',
            'year',
            'Composition of EV Sales by Vehicle Type'
        )
        
        st.plotly_chart(composition_fig, use_container_width=True)
        
        # Add composition insights
        st.markdown("""
        **Composition Insights:**
        - The chart shows how the mix of electric vehicle types has evolved over time.
        - Battery Electric Vehicles (BEVs) vs. Plug-in Hybrid Electric Vehicles (PHEVs) trends indicate market maturity.
        - Shifts in composition often reflect changing consumer preferences and technological improvements.
        """)
    
    # Additional market analysis
    st.header("Market Penetration Analysis")
    
    st.markdown("""
    Market penetration refers to how deeply EVs have penetrated the overall vehicle market.
    This is influenced by several factors:
    
    - **Affordability**: Price parity with conventional vehicles
    - **Infrastructure**: Availability of charging stations
    - **Range**: Battery technology improvements
    - **Model Availability**: Diversity of EV options
    - **Consumer Awareness**: Education and exposure to EVs
    
    Markets with high penetration typically have addressed these factors through policy support, 
    infrastructure investment, and consumer incentives.
    """)
    
    # Milestone projections
    st.header("Market Share Milestones")
    
    st.markdown("""
    Several key market share milestones are significant in the EV transition:
    
    - **10% Market Share**: Generally considered the early mainstream adoption threshold
    - **25% Market Share**: Signals significant market transformation
    - **50% Market Share**: Represents the tipping point where EVs become the dominant technology
    - **100% Market Share**: Full electrification of new vehicle sales
    
    Different regions are projected to reach these milestones at different times:
    
    | Region | 25% Milestone | 50% Milestone | 100% Milestone |
    |--------|--------------|--------------|----------------|
    | Norway | Achieved     | Achieved     | ~2025          |
    | Europe | ~2025        | ~2030-2035   | 2035-2040      |
    | China  | ~2025-2027   | ~2035        | 2040           |
    | USA    | ~2027-2030   | ~2035-2040   | 2040-2050      |
    | Global | ~2027-2030   | ~2035-2040   | 2050           |
    
    These projections vary based on policy commitments, industry investments, and market conditions.
    """)
