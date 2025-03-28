import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.forecasting import forecast_linear, forecast_polynomial, forecast_by_region, plot_forecast

def app():
    st.title("EV Adoption Forecasting")
    
    # Check if data is loaded
    if 'cleaned_data' not in st.session_state or st.session_state.cleaned_data is None:
        st.warning("Please load data from the main page first.")
        return
    
    data = st.session_state.cleaned_data
    
    st.markdown("""
    This page provides forecasting of future EV adoption trends based on historical data.
    The forecasts use simple statistical models and should be interpreted as projections
    assuming current trends continue, not as definitive predictions.
    """)
    
    # Forecasting parameters
    st.header("Forecasting Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        forecast_periods = st.number_input(
            "Forecast Periods (Years)",
            min_value=1,
            max_value=20,
            value=5
        )
    
    with col2:
        forecast_method = st.selectbox(
            "Forecasting Method",
            options=["Linear", "Polynomial"],
            index=0
        )
    
    with col3:
        if forecast_method == "Polynomial":
            polynomial_degree = st.number_input(
                "Polynomial Degree",
                min_value=2,
                max_value=5,
                value=2
            )
        else:
            polynomial_degree = 2  # Default value, not used for linear
    
    # Global forecast
    st.header("Global EV Adoption Forecast")
    
    # Aggregate data by year
    global_data = data.groupby('year')['sales'].sum().reset_index()
    
    # Perform forecasting based on selected method
    if forecast_method == "Polynomial":
        forecast_df, metrics, _ = forecast_polynomial(
            global_data,
            'year',
            'sales',
            forecast_periods,
            polynomial_degree
        )
    else:
        forecast_df, metrics, _ = forecast_linear(
            global_data,
            'year',
            'sales',
            forecast_periods
        )
    
    # Display forecast
    if not forecast_df.empty:
        # Plot forecast
        forecast_fig = plot_forecast(
            forecast_df,
            'year',
            'sales',
            f'Global EV Sales Forecast ({forecast_method} Model)'
        )
        st.plotly_chart(forecast_fig, use_container_width=True)
        
        # Display model metrics
        st.subheader("Model Metrics")
        
        metrics_df = pd.DataFrame({
            'Metric': list(metrics.keys()),
            'Value': list(metrics.values())
        })
        
        st.table(metrics_df)
        
        # Forecast table
        st.subheader("Forecast Values")
        
        # Format the forecast data for display
        display_forecast = forecast_df.copy()
        display_forecast['sales'] = display_forecast['sales'].round(0).astype(int)
        display_forecast.columns = ['Year', 'Sales', 'Type']
        
        # Display only future values
        future_forecast = display_forecast[display_forecast['Type'] == 'forecast']
        st.table(future_forecast[['Year', 'Sales']])
        
        # Add forecast insights
        st.markdown("""
        **Forecast Insights:**
        - This forecast assumes past trends will continue, which may not account for disruptive changes.
        - Key factors that could accelerate adoption: technology breakthroughs, stronger policies, price reductions.
        - Factors that could slow adoption: supply chain constraints, infrastructure limitations, policy changes.
        - The forecast uncertainty increases the further into the future we project.
        """)
    else:
        st.error("Insufficient data for forecasting. Please ensure you have at least 3 years of historical data.")
    
    # Regional forecasts
    st.header("Regional Adoption Forecasts")
    
    # Select regions for forecasting
    forecast_regions = st.multiselect(
        "Select Regions to Forecast",
        options=sorted(data['region'].unique()),
        default=sorted(data['region'].unique())[:3] if len(data['region'].unique()) > 3 else sorted(data['region'].unique())
    )
    
    if forecast_regions:
        # Filter data for selected regions
        region_data = data[data['region'].isin(forecast_regions)]
        
        # Perform forecasting for each region
        method = forecast_method.lower()
        regional_forecasts = forecast_by_region(
            region_data,
            'region',
            'year',
            'sales',
            forecast_periods,
            method
        )
        
        if not regional_forecasts.empty:
            # Create visualization
            import plotly.graph_objects as go
            
            fig = go.Figure()
            
            # Add traces for each region and forecast type
            for region in forecast_regions:
                region_forecast = regional_forecasts[regional_forecasts['region'] == region]
                
                if region_forecast.empty:
                    continue
                
                # Historical data
                historical = region_forecast[region_forecast['type'] == 'historical']
                forecast = region_forecast[region_forecast['type'] == 'forecast']
                
                # Add historical line
                fig.add_trace(go.Scatter(
                    x=historical['year'],
                    y=historical['sales'],
                    mode='lines',
                    name=f'{region} (Historical)',
                    line=dict(width=2)
                ))
                
                # Add forecast line
                fig.add_trace(go.Scatter(
                    x=forecast['year'],
                    y=forecast['sales'],
                    mode='lines+markers',
                    name=f'{region} (Forecast)',
                    line=dict(dash='dash', width=2)
                ))
            
            fig.update_layout(
                title=f'Regional EV Sales Forecasts ({forecast_method} Model)',
                xaxis_title='Year',
                yaxis_title='Sales',
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display projections
            st.subheader("Regional Projections")
            
            # Calculate projected values for milestone years
            latest_year = data['year'].max()
            milestone_years = [latest_year + 5, latest_year + 10]
            
            milestone_data = []
            
            for region in forecast_regions:
                region_forecast = regional_forecasts[
                    (regional_forecasts['region'] == region) & 
                    (regional_forecasts['type'] == 'forecast')
                ]
                
                if region_forecast.empty:
                    continue
                
                for year in milestone_years:
                    if year in region_forecast['year'].values:
                        projected_sales = region_forecast[region_forecast['year'] == year]['sales'].values[0]
                        milestone_data.append({
                            'Region': region,
                            'Year': year,
                            'Projected Sales': int(round(projected_sales))
                        })
            
            if milestone_data:
                milestone_df = pd.DataFrame(milestone_data)
                st.table(milestone_df)
            else:
                st.info("No milestone projections available for the selected regions.")
        else:
            st.warning("Insufficient data for regional forecasting. Each region needs at least 3 years of historical data.")
    else:
        st.info("Please select at least one region for forecasting.")
    
    # Forecast limitations
    st.header("Forecast Limitations")
    
    st.markdown("""
    It's important to understand the limitations of these forecasts:
    
    1. **Simple Models**: These forecasts use statistical models that don't account for complex market dynamics.
    
    2. **Assumes Pattern Continuation**: The forecasts assume historical patterns will continue, which may not be true in a rapidly evolving market.
    
    3. **Doesn't Account For**:
       - Supply chain constraints
       - Policy changes (new incentives or regulations)
       - Technological breakthroughs
       - Consumer preference shifts
       - Charging infrastructure growth
       - Competitive dynamics
    
    4. **Uncertainty Increases**: The further into the future we forecast, the less reliable the projections become.
    
    These forecasts should be treated as one possible scenario based on historical trends, not as definitive predictions.
    """)
