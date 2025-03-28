import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from utils.data_processor import calculate_market_share, get_top_regions, calculate_growth_rates
from utils.data_visualizer import (plot_global_trends, plot_regional_comparison, 
                                  create_choropleth_map, plot_market_share_evolution, 
                                  create_stacked_area_chart, plot_growth_rates)
from utils.forecasting import forecast_linear, forecast_polynomial, forecast_by_region, plot_forecast

# Overview page functionality
def overview_page():
    st.header("Global EV Adoption Overview")
    
    if 'cleaned_data' not in st.session_state or st.session_state.cleaned_data is None:
        st.warning("Please load data first")
        return
    
    data = st.session_state.cleaned_data
    
    # Global metrics
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    # Latest year in the data
    latest_year = data['year'].max()
    
    # Total EV sales in the latest year
    total_sales = data[data['year'] == latest_year]['sales'].sum()
    col1.metric("Total EV Sales (Latest Year)", f"{total_sales:,.0f}")
    
    # Growth from previous year
    prev_year = latest_year - 1
    prev_year_sales = data[data['year'] == prev_year]['sales'].sum()
    
    if prev_year_sales > 0:
        growth_pct = (total_sales - prev_year_sales) / prev_year_sales * 100
        col2.metric("Year-over-Year Growth", f"{growth_pct:.1f}%")
    else:
        col2.metric("Year-over-Year Growth", "N/A")
    
    # Number of regions
    region_count = data['region'].nunique()
    col3.metric("Regions Analyzed", region_count)
    
    # Top region by sales
    top_region_data = get_top_regions(data, latest_year, 'sales', 1)
    if not top_region_data.empty:
        top_region = top_region_data.iloc[0]['region']
        top_region_sales = top_region_data.iloc[0]['sales']
        col4.metric("Top Region", f"{top_region} ({top_region_sales:,.0f} units)")
    
    # Global trends chart
    st.subheader("Global EV Adoption Trend")
    fig = plot_global_trends(data, 'sales', 'Global EV Sales Over Time')
    st.plotly_chart(fig, use_container_width=True)
    
    # Show market share if available
    if 'market_share' in data.columns:
        st.subheader("EV Market Share Trend")
        fig = plot_global_trends(data, 'market_share', 'Global EV Market Share Over Time')
        st.plotly_chart(fig, use_container_width=True)
    
    # Regional distribution in latest year
    st.subheader(f"Regional Distribution ({latest_year})")
    col1, col2 = st.columns(2)
    
    with col1:
        latest_year_data = data[data['year'] == latest_year]
        fig = plot_regional_comparison(latest_year_data, latest_year, 'sales')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'ev_type' in data.columns:
            # Vehicle type distribution
            vehicle_type_data = data[data['year'] == latest_year].groupby('ev_type')['sales'].sum().reset_index()
            fig = px.pie(
                vehicle_type_data, 
                values='sales', 
                names='ev_type',
                title=f'EV Types Distribution ({latest_year})',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig, use_container_width=True)

# Regional analysis page functionality
def regional_analysis_page():
    st.header("Regional EV Adoption Analysis")
    
    if 'cleaned_data' not in st.session_state or st.session_state.cleaned_data is None:
        st.warning("Please load data first")
        return
    
    data = st.session_state.cleaned_data
    
    # Map visualization
    st.subheader("Geographic Distribution")
    
    # Year selector for the map
    years = sorted(data['year'].unique())
    selected_year = st.select_slider("Select Year for Map", options=years, value=years[-1])
    
    year_data = data[data['year'] == selected_year]
    
    # Create and display choropleth map
    fig = create_choropleth_map(year_data, 'sales', f'EV Sales by Region ({selected_year})')
    st.plotly_chart(fig, use_container_width=True)
    
    # Regional comparison
    st.subheader("Regional Comparison")
    
    # Metric selector
    metric = st.radio("Select Metric", ["Sales Volume", "Year-over-Year Growth"], horizontal=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Regions")
        
        if metric == "Sales Volume":
            top_regions = get_top_regions(data, selected_year, 'sales', 10)
            if not top_regions.empty:
                fig = px.bar(
                    top_regions,
                    x='sales',
                    y='region',
                    orientation='h',
                    title=f"Top Regions by EV Sales ({selected_year})",
                    labels={'sales': 'Sales Volume', 'region': 'Region'},
                    color='sales',
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            # Year-over-Year Growth
            growth_data = calculate_growth_rates(data)
            growth_year_data = growth_data[growth_data['year'] == selected_year].sort_values('growth_rate', ascending=False).head(10)
            
            if not growth_year_data.empty:
                fig = px.bar(
                    growth_year_data,
                    x='growth_rate',
                    y='region',
                    orientation='h',
                    title=f"Top Regions by EV Sales Growth ({selected_year})",
                    labels={'growth_rate': 'Growth Rate (%)', 'region': 'Region'},
                    color='growth_rate',
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                fig.update_layout(xaxis_ticksuffix="%")
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Regional Trends")
        
        # Region selector for trend analysis
        top_regions_list = data.groupby('region')['sales'].sum().sort_values(ascending=False).head(10).index.tolist()
        selected_regions = st.multiselect(
            "Select Regions to Compare",
            options=sorted(data['region'].unique()),
            default=top_regions_list[:5] if top_regions_list else None
        )
        
        if selected_regions:
            region_data = data[data['region'].isin(selected_regions)]
            
            if metric == "Sales Volume":
                fig = px.line(
                    region_data, 
                    x='year', 
                    y='sales', 
                    color='region',
                    markers=True,
                    title='EV Sales Trends by Region',
                    labels={'sales': 'Sales Volume', 'year': 'Year', 'region': 'Region'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Growth rate trends
                growth_data = calculate_growth_rates(data)
                region_growth_data = growth_data[growth_data['region'].isin(selected_regions)]
                
                if not region_growth_data.empty:
                    fig = px.line(
                        region_growth_data, 
                        x='year', 
                        y='growth_rate', 
                        color='region',
                        markers=True,
                        title='EV Sales Growth Trends by Region',
                        labels={'growth_rate': 'Growth Rate (%)', 'year': 'Year', 'region': 'Region'}
                    )
                    fig.update_layout(yaxis_ticksuffix="%")
                    st.plotly_chart(fig, use_container_width=True)

# Market share page functionality
def market_share_page():
    st.header("EV Market Share Analysis")
    
    if 'cleaned_data' not in st.session_state or st.session_state.cleaned_data is None:
        st.warning("Please load data first")
        return
    
    data = st.session_state.cleaned_data
    
    # Calculate market share if not already present
    if 'market_share' not in data.columns and 'total_vehicle_sales' in data.columns:
        data = calculate_market_share(data)
    
    # Check if market share data is available
    if 'market_share' in data.columns:
        # Global market share evolution
        st.subheader("Global EV Market Share Evolution")
        fig = plot_market_share_evolution(data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Regional market share comparison
        st.subheader("Regional Market Share Comparison")
        
        # Year selector
        years = sorted(data['year'].unique())
        selected_year = st.select_slider("Select Year", options=years, value=years[-1])
        
        year_data = data[data['year'] == selected_year]
        
        fig = plot_regional_comparison(year_data, selected_year, 'market_share')
        st.plotly_chart(fig, use_container_width=True)
        
        # Market share milestone calculator
        st.subheader("Market Share Milestone Calculator")
        st.markdown("""
        This tool calculates when specific regions might reach important EV market share milestones
        based on historical growth patterns.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Region selection
            available_regions = sorted(data['region'].unique())
            calc_region = st.selectbox("Select Region", options=available_regions)
            
            # Target market share
            target_share = st.slider("Target Market Share (%)", min_value=10, max_value=100, value=50, step=5)
            
            # Model type
            model_type = st.radio("Forecasting Model", ["Linear", "Polynomial"], horizontal=True)
            
        with col2:
            if calc_region:
                region_data = data[data['region'] == calc_region]
                
                if 'market_share' in region_data.columns and not region_data.empty:
                    latest_year = region_data['year'].max()
                    latest_share = region_data[region_data['year'] == latest_year]['market_share'].values[0]
                    
                    st.metric("Current Market Share", f"{latest_share:.1f}%", 
                             f"{latest_share - region_data[region_data['year'] == latest_year-1]['market_share'].values[0]:.1f}% from previous year" 
                             if latest_year > region_data['year'].min() else None)
                    
                    # Calculate forecast
                    forecast_periods = 30  # Look ahead up to 30 years
                    
                    if model_type == "Linear":
                        forecast_df, metrics, _ = forecast_linear(region_data, 'year', 'market_share', forecast_periods)
                    else:
                        forecast_df, metrics, _ = forecast_polynomial(region_data, 'year', 'market_share', forecast_periods)
                    
                    if not forecast_df.empty:
                        # Find when target is reached
                        future_data = forecast_df[forecast_df['type'] == 'forecast']
                        target_reached = future_data[future_data['market_share'] >= target_share]
                        
                        if not target_reached.empty:
                            target_year = int(target_reached.iloc[0]['year'])
                            target_value = target_reached.iloc[0]['market_share']
                            years_to_target = target_year - latest_year
                            
                            st.success(f"Based on current trends, {calc_region} could reach {target_share}% EV market share by **{target_year}** ({years_to_target} years from now).")
                            
                            # Show forecast chart
                            fig = plot_forecast(forecast_df, 'year', 'market_share', 
                                              f'Market Share Forecast for {calc_region}')
                            
                            # Add a target line
                            fig.add_hline(y=target_share, line_dash="dash", line_color="green",
                                        annotation_text=f"Target: {target_share}%")
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning(f"The target of {target_share}% may not be reached within the next {forecast_periods} years based on current trends.")
                            
                            # Still show the forecast chart
                            fig = plot_forecast(forecast_df, 'year', 'market_share', 
                                              f'Market Share Forecast for {calc_region}')
                            
                            # Add a target line
                            fig.add_hline(y=target_share, line_dash="dash", line_color="green",
                                        annotation_text=f"Target: {target_share}%")
                            
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Unable to create forecast with the available data. Try a different region or model type.")
                else:
                    st.error("Market share data is not available for this region.")
    else:
        st.warning("Market share data is not available. Please upload data that includes total vehicle sales.")
        
        # Create dummy data for demonstration
        st.subheader("Sample Market Share Visualization")
        st.markdown("Below is a sample visualization of what market share analysis would look like with appropriate data:")
        
        # Create dummy market share data
        years = range(2010, 2024)
        global_share = [0.1, 0.2, 0.3, 0.5, 0.8, 1.2, 1.8, 2.5, 3.3, 4.2, 5.1, 7.0, 9.2, 12.5]
        
        dummy_data = pd.DataFrame({
            'year': years,
            'market_share': global_share
        })
        
        fig = px.line(
            dummy_data, 
            x='year', 
            y='market_share',
            markers=True,
            title='Sample: Global EV Market Share Evolution',
            labels={'market_share': 'Market Share (%)', 'year': 'Year'}
        )
        fig.update_layout(yaxis_ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("Upload data with 'total_vehicle_sales' to enable market share analysis.")

# Forecasting page functionality
def forecasting_page():
    st.header("EV Adoption Forecasting")
    
    if 'cleaned_data' not in st.session_state or st.session_state.cleaned_data is None:
        st.warning("Please load data first")
        return
    
    data = st.session_state.cleaned_data
    
    # Forecasting controls
    st.subheader("Forecast Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Forecast scope
        forecast_scope = st.radio("Forecast Scope", ["Global", "Regional"], horizontal=True)
        
        # Number of periods
        periods = st.slider("Forecast Periods (Years)", min_value=1, max_value=20, value=10)
    
    with col2:
        # Target metric
        metric_options = ["sales"]
        if 'market_share' in data.columns:
            metric_options.append("market_share")
        
        forecast_metric = st.selectbox(
            "Target Metric", 
            options=metric_options,
            format_func=lambda x: "Sales Volume" if x == "sales" else "Market Share (%)"
        )
        
        # Model type
        model_type = st.radio("Model Type", ["Linear", "Polynomial"], horizontal=True)
        
        if model_type == "Polynomial":
            degree = st.slider("Polynomial Degree", min_value=2, max_value=5, value=2)
        else:
            degree = 1  # Default for linear
    
    with col3:
        if forecast_scope == "Regional":
            # Region selection for regional forecasting
            available_regions = sorted(data['region'].unique())
            selected_regions = st.multiselect(
                "Select Regions", 
                options=available_regions,
                default=available_regions[:3] if len(available_regions) >= 3 else available_regions
            )
        else:
            # For global forecasting, include all regions
            selected_regions = sorted(data['region'].unique())
            st.info("Global forecast combines data from all regions")
    
    # Generate forecast
    st.subheader("EV Adoption Forecast")
    
    try:
        # Filter data for selected regions
        if forecast_scope == "Regional" and selected_regions:
            filtered_data = data[data['region'].isin(selected_regions)]
        else:
            filtered_data = data  # Use all data for global forecasting
        
        if model_type == "Linear":
            if forecast_scope == "Global":
                # Aggregate data globally and forecast
                global_data = filtered_data.groupby('year')[forecast_metric].sum().reset_index()
                global_data = pd.DataFrame({
                    'year': global_data['year'],
                    forecast_metric: global_data[forecast_metric],
                    'region': 'Global'  # Add dummy region column
                })
                
                forecast_df, metrics, _ = forecast_linear(global_data, 'year', forecast_metric, periods)
                
                if not forecast_df.empty:
                    forecast_df['region'] = 'Global'  # Keep dummy region for consistency
                    
                    st.write(f"Forecast Metrics: R² = {metrics['r2']:.4f}, RMSE = {metrics['rmse']:.2f}")
                    
                    # Create visualization
                    fig = plot_forecast(forecast_df, 'year', forecast_metric,
                                      f'Global {forecast_metric.capitalize()} Forecast')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                # Regional forecasting
                regional_forecasts = forecast_by_region(
                    filtered_data, 'region', 'year', forecast_metric, periods, 'linear'
                )
                
                if not regional_forecasts.empty:
                    # Plot multi-region forecast
                    fig = px.line(
                        regional_forecasts,
                        x='year',
                        y=forecast_metric,
                        color='region',
                        line_dash='type',
                        title=f'Regional {forecast_metric.capitalize()} Forecast',
                        labels={forecast_metric: forecast_metric.capitalize(), 'year': 'Year'}
                    )
                    
                    # Customize line styles
                    for i, trace in enumerate(fig.data):
                        if trace.line.dash == 'forecast':
                            trace.line.width = 2
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Insufficient data to generate regional forecasts.")
        else:
            # Polynomial forecasting
            if forecast_scope == "Global":
                # Aggregate data globally and forecast
                global_data = filtered_data.groupby('year')[forecast_metric].sum().reset_index()
                global_data = pd.DataFrame({
                    'year': global_data['year'],
                    forecast_metric: global_data[forecast_metric],
                    'region': 'Global'  # Add dummy region column
                })
                
                forecast_df, metrics, _ = forecast_polynomial(global_data, 'year', forecast_metric, periods, degree)
                
                if not forecast_df.empty:
                    forecast_df['region'] = 'Global'  # Keep dummy region for consistency
                    
                    st.write(f"Forecast Metrics: R² = {metrics['r2']:.4f}, RMSE = {metrics['rmse']:.2f}")
                    
                    # Create visualization
                    fig = plot_forecast(forecast_df, 'year', forecast_metric,
                                      f'Global {forecast_metric.capitalize()} Forecast (Polynomial Degree {degree})')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                # Regional polynomial forecasting
                regional_forecasts = pd.DataFrame()  # Initialize empty DataFrame
                
                for region in selected_regions:
                    region_data = filtered_data[filtered_data['region'] == region]
                    
                    if len(region_data) >= degree + 1:  # Ensure enough data points for the polynomial degree
                        forecast_df, _, _ = forecast_polynomial(region_data, 'year', forecast_metric, periods, degree)
                        
                        if not forecast_df.empty:
                            forecast_df['region'] = region
                            regional_forecasts = pd.concat([regional_forecasts, forecast_df], ignore_index=True)
                
                if not regional_forecasts.empty:
                    # Plot multi-region forecast
                    fig = px.line(
                        regional_forecasts,
                        x='year',
                        y=forecast_metric,
                        color='region',
                        line_dash='type',
                        title=f'Regional {forecast_metric.capitalize()} Forecast (Polynomial Degree {degree})',
                        labels={forecast_metric: forecast_metric.capitalize(), 'year': 'Year'}
                    )
                    
                    # Customize line styles
                    for i, trace in enumerate(fig.data):
                        if trace.line.dash == 'forecast':
                            trace.line.width = 2
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Insufficient data to generate polynomial forecasts for the selected regions.")
                    
        # Add forecast interpretation
        with st.expander("Forecast Interpretation"):
            st.markdown(f"""
            ### Interpreting the Forecast
            
            This forecast uses {'linear regression' if model_type == 'Linear' else f'polynomial regression (degree {degree})'} 
            to project future EV {'sales' if forecast_metric == 'sales' else 'market share'} based on historical trends.
            
            #### Key Assumptions:
            
            - The forecast assumes that past growth patterns will continue into the future.
            - It does not account for potential market disruptions, policy changes, or technology breakthroughs.
            - {'Higher degree polynomials may overfit to historical data patterns.' if model_type == 'Polynomial' else 'Linear projections may oversimplify complex market dynamics.'}
            
            #### Recommendation:
            
            Use these forecasts as one potential scenario rather than a definitive prediction. For robust planning, 
            consider supplementing with multiple scenarios and additional qualitative factors.
            """)
    except Exception as e:
        st.error(f"Error generating forecast: {str(e)}")
        st.code(str(e), language="python")