import streamlit as st
import pandas as pd
import numpy as np
from utils.data_visualizer import plot_global_trends, plot_regional_comparison, plot_growth_rates
from utils.data_processor import calculate_growth_rates

def app():
    st.title("Global EV Adoption Overview")
    
    # Check if data is loaded
    if 'cleaned_data' not in st.session_state or st.session_state.cleaned_data is None:
        st.warning("Please load data from the main page first.")
        return
    
    data = st.session_state.cleaned_data
    
    st.markdown("""
    This page provides an overview of global EV adoption trends, highlighting key metrics and patterns over time.
    """)
    
    # Key metrics and summary statistics
    st.header("Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    latest_year = data['year'].max()
    earliest_year = data['year'].min()
    total_years = latest_year - earliest_year + 1
    
    # Calculate total sales
    total_sales = data['sales'].sum()
    latest_year_sales = data[data['year'] == latest_year]['sales'].sum()
    
    with col1:
        st.metric(
            label="Total EV Sales",
            value=f"{total_sales:,.0f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label=f"Sales in {latest_year}",
            value=f"{latest_year_sales:,.0f}",
            delta=None
        )
    
    with col3:
        # Calculate CAGR if possible
        if total_years > 1:
            first_year_sales = data[data['year'] == earliest_year]['sales'].sum()
            if first_year_sales > 0:
                cagr = (((latest_year_sales / first_year_sales) ** (1 / (total_years - 1))) - 1) * 100
                st.metric(
                    label=f"CAGR ({earliest_year}-{latest_year})",
                    value=f"{cagr:.1f}%",
                    delta=None
                )
            else:
                st.metric(
                    label="Years of Data",
                    value=f"{total_years}",
                    delta=None
                )
        else:
            st.metric(
                label="Years of Data",
                value=f"{total_years}",
                delta=None
            )
    
    # Global trends
    st.header("Global Adoption Trends")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Sales Trend", "Growth Rates", "Regional Leaders"])
    
    with tab1:
        st.subheader("EV Sales Over Time")
        sales_fig = plot_global_trends(data, 'sales', 'Global EV Sales Over Time')
        st.plotly_chart(sales_fig, use_container_width=True)
        
        # Add some insights about the trend
        st.markdown("""
        **Insights:**
        - The chart shows the overall trajectory of EV sales globally over time.
        - Note any significant increases or plateaus in the trend.
        - Major policy changes or technological advances often correspond with changes in the growth curve.
        """)
    
    with tab2:
        st.subheader("Year-over-Year Growth Rates")
        
        # Calculate growth rates
        growth_data = calculate_growth_rates(data)
        
        if not growth_data.empty:
            growth_fig = plot_growth_rates(growth_data)
            st.plotly_chart(growth_fig, use_container_width=True)
            
            # Add some insights about growth rates
            st.markdown("""
            **Insights:**
            - Growth rates show the acceleration or deceleration of EV adoption.
            - Very high growth rates often occur in early adoption phases with small base numbers.
            - More mature markets typically show more modest but sustainable growth rates.
            """)
        else:
            st.info("Insufficient data to calculate meaningful growth rates.")
    
    with tab3:
        st.subheader("Regional Leaders")
        
        # Select year for comparison
        selected_year = st.slider(
            "Select Year for Regional Comparison",
            min_value=int(data['year'].min()),
            max_value=int(data['year'].max()),
            value=int(data['year'].max())
        )
        
        comparison_fig = plot_regional_comparison(data, selected_year, 'sales')
        st.plotly_chart(comparison_fig, use_container_width=True)
        
        # Add some insights about regional comparison
        st.markdown("""
        **Insights:**
        - The chart shows which regions lead in EV adoption for the selected year.
        - Regional differences may reflect policy environments, consumer preferences, and infrastructure availability.
        - Compare the distribution year over year to see if leadership positions are changing.
        """)
    
    # Historical milestones
    st.header("Key Milestones in EV Adoption")
    st.markdown("""
    Electric vehicle adoption has seen several key milestones:
    
    - **Early 2010s**: First mass-market EVs introduced (Nissan Leaf, Tesla Model S)
    - **2015-2016**: EV sales surpass 1 million vehicles globally
    - **2018**: Multiple countries announce future bans on internal combustion engines
    - **2020**: EVs begin to reach price parity with conventional vehicles in some segments
    - **2023**: EVs reached approximately 18% of global new car sales
    
    These milestones reflect the transition of electric vehicles from niche products to mainstream transportation options.
    """)
