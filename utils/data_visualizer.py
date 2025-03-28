import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

def plot_global_trends(data, metric='sales', title=''):
    """
    Creates a line chart showing global trends over time.
    
    Args:
        data (pandas.DataFrame): Cleaned EV adoption data
        metric (str): The metric to visualize (e.g., 'sales', 'market_share')
        title (str): Title for the plot
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    if 'year' not in data.columns or metric not in data.columns:
        # Create an empty figure with a message if data is missing
        fig = go.Figure()
        fig.add_annotation(
            text="Data required for visualization is missing",
            showarrow=False,
            font=dict(size=14)
        )
        return fig
    
    # Aggregate data by year
    yearly_data = data.groupby('year')[metric].sum().reset_index()
    
    # Create line chart
    fig = px.line(
        yearly_data, 
        x='year', 
        y=metric,
        labels={metric: metric.capitalize(), 'year': 'Year'},
        title=title or f'Global {metric.capitalize()} Trend'
    )
    
    fig.update_layout(
        xaxis=dict(tickmode='linear'),
        hovermode='x unified'
    )
    
    return fig

def plot_regional_comparison(data, year, metric='sales'):
    """
    Creates a bar chart comparing regions for a specific year.
    
    Args:
        data (pandas.DataFrame): Cleaned EV adoption data
        year (int): The year to visualize
        metric (str): The metric to visualize (e.g., 'sales', 'market_share')
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    if 'region' not in data.columns or metric not in data.columns:
        # Create an empty figure with a message if data is missing
        fig = go.Figure()
        fig.add_annotation(
            text="Data required for visualization is missing",
            showarrow=False,
            font=dict(size=14)
        )
        return fig
    
    # Filter data for the specified year
    year_data = data[data['year'] == year]
    
    # Group by region and calculate the sum of the metric
    region_data = year_data.groupby('region')[metric].sum().reset_index()
    region_data = region_data.sort_values(metric, ascending=False)
    
    # Create bar chart
    fig = px.bar(
        region_data,
        x='region',
        y=metric,
        color=metric,
        labels={metric: metric.capitalize(), 'region': 'Region'},
        title=f'Regional Comparison of {metric.capitalize()} in {year}',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis={'categoryorder': 'total descending'},
        hovermode='closest'
    )
    
    return fig

def create_choropleth_map(data, metric='sales', title=''):
    """
    Creates a choropleth map visualizing the metric by region.
    
    Args:
        data (pandas.DataFrame): Cleaned EV adoption data
        metric (str): The metric to visualize (e.g., 'sales', 'market_share')
        title (str): Title for the plot
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    if 'region' not in data.columns or metric not in data.columns:
        # Create an empty figure with a message if data is missing
        fig = go.Figure()
        fig.add_annotation(
            text="Data required for visualization is missing",
            showarrow=False,
            font=dict(size=14)
        )
        return fig
    
    # Aggregate data by region
    region_data = data.groupby('region')[metric].sum().reset_index()
    
    # Create choropleth map
    fig = px.choropleth(
        region_data,
        locations='region',
        locationmode='country names',
        color=metric,
        hover_name='region',
        color_continuous_scale='Viridis',
        labels={metric: metric.capitalize()},
        title=title or f'{metric.capitalize()} by Region'
    )
    
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth'
        )
    )
    
    return fig

def plot_market_share_evolution(data):
    """
    Creates a line chart showing the evolution of EV market share over time by region.
    
    Args:
        data (pandas.DataFrame): Cleaned EV adoption data with market share
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    if 'year' not in data.columns or 'region' not in data.columns or 'market_share' not in data.columns:
        # Create an empty figure with a message if data is missing
        fig = go.Figure()
        fig.add_annotation(
            text="Market share data is missing",
            showarrow=False,
            font=dict(size=14)
        )
        return fig
    
    # Calculate average market share by year and region
    market_data = data.groupby(['year', 'region'])['market_share'].mean().reset_index()
    
    # Create line chart
    fig = px.line(
        market_data,
        x='year',
        y='market_share',
        color='region',
        labels={'market_share': 'Market Share (%)', 'year': 'Year', 'region': 'Region'},
        title='Evolution of EV Market Share by Region'
    )
    
    fig.update_layout(
        xaxis=dict(tickmode='linear'),
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def plot_growth_rates(growth_data):
    """
    Creates a visualization of year-over-year growth rates.
    
    Args:
        growth_data (pandas.DataFrame): DataFrame containing growth rate data
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    if growth_data.empty or 'growth_rate' not in growth_data.columns:
        # Create an empty figure with a message if data is missing
        fig = go.Figure()
        fig.add_annotation(
            text="Growth rate data is missing or insufficient",
            showarrow=False,
            font=dict(size=14)
        )
        return fig
    
    # Filter growth rates to remove extreme outliers
    valid_growth = growth_data[growth_data['growth_rate'].between(-100, 200)]
    
    if valid_growth.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Not enough valid growth rate data after filtering outliers",
            showarrow=False,
            font=dict(size=14)
        )
        return fig
    
    # Create line chart
    fig = px.line(
        valid_growth,
        x='year',
        y='growth_rate',
        color='region',
        labels={'growth_rate': 'YoY Growth Rate (%)', 'year': 'Year', 'region': 'Region'},
        title='Year-over-Year Growth in EV Adoption'
    )
    
    fig.update_layout(
        xaxis=dict(tickmode='linear'),
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_stacked_area_chart(data, category_col, value_col, time_col='year', title=''):
    """
    Creates a stacked area chart to show composition over time.
    
    Args:
        data (pandas.DataFrame): Cleaned EV adoption data
        category_col (str): Column name for categories (e.g., 'vehicle_type')
        value_col (str): Column name for values (e.g., 'sales')
        time_col (str): Column name for time periods (default: 'year')
        title (str): Title for the plot
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    if category_col not in data.columns or value_col not in data.columns or time_col not in data.columns:
        # Create an empty figure with a message if data is missing
        fig = go.Figure()
        fig.add_annotation(
            text="Data required for visualization is missing",
            showarrow=False,
            font=dict(size=14)
        )
        return fig
    
    # Group by time and category
    grouped_data = data.groupby([time_col, category_col])[value_col].sum().reset_index()
    
    # Create stacked area chart
    fig = px.area(
        grouped_data,
        x=time_col,
        y=value_col,
        color=category_col,
        labels={value_col: value_col.capitalize(), time_col: time_col.capitalize(), category_col: category_col.capitalize()},
        title=title or f'Composition of {value_col.capitalize()} by {category_col.capitalize()} Over Time'
    )
    
    fig.update_layout(
        xaxis=dict(tickmode='linear'),
        hovermode='x unified'
    )
    
    return fig
