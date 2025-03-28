import pandas as pd
import numpy as np

def clean_data(data):
    """
    Cleans and prepares the EV adoption data for analysis.
    
    Args:
        data (pandas.DataFrame): Raw EV adoption data
        
    Returns:
        pandas.DataFrame: Cleaned EV adoption data
    """
    # Make a copy to avoid modifying the original data
    cleaned_data = data.copy()
    
    # Handle missing values
    if 'sales' in cleaned_data.columns:
        cleaned_data['sales'] = cleaned_data['sales'].fillna(0)
    
    if 'market_share' in cleaned_data.columns:
        cleaned_data['market_share'] = cleaned_data['market_share'].fillna(0)
    
    # Ensure year is an integer
    if 'year' in cleaned_data.columns:
        cleaned_data['year'] = pd.to_numeric(cleaned_data['year'], errors='coerce').fillna(0).astype(int)
    
    # Ensure region names are standardized
    if 'region' in cleaned_data.columns:
        cleaned_data['region'] = cleaned_data['region'].str.strip()
    
    return cleaned_data

def calculate_growth_rates(data):
    """
    Calculates year-over-year growth rates for EV sales by region.
    
    Args:
        data (pandas.DataFrame): Cleaned EV adoption data
        
    Returns:
        pandas.DataFrame: Data with growth rates
    """
    if 'year' not in data.columns or 'region' not in data.columns or 'sales' not in data.columns:
        return pd.DataFrame()  # Return empty DataFrame if required columns are missing
    
    # Group by region and year, and calculate sales sum
    yearly_sales = data.groupby(['region', 'year'])['sales'].sum().reset_index()
    
    # Calculate growth rates for each region
    growth_rates = []
    
    for region in yearly_sales['region'].unique():
        region_data = yearly_sales[yearly_sales['region'] == region].sort_values('year')
        
        if len(region_data) <= 1:
            continue  # Skip regions with only one year of data
        
        # Calculate year-over-year growth
        for i in range(1, len(region_data)):
            prev_year = region_data.iloc[i-1]['year']
            curr_year = region_data.iloc[i]['year']
            prev_sales = region_data.iloc[i-1]['sales']
            curr_sales = region_data.iloc[i]['sales']
            
            if prev_sales > 0:  # Avoid division by zero
                growth_rate = ((curr_sales - prev_sales) / prev_sales) * 100
            else:
                growth_rate = np.nan  # Mark as NaN if previous sales were zero
            
            growth_rates.append({
                'region': region,
                'year': curr_year,
                'growth_rate': growth_rate
            })
    
    return pd.DataFrame(growth_rates)

def calculate_market_share(data):
    """
    Calculates market share of EVs if total vehicle sales are available.
    
    Args:
        data (pandas.DataFrame): EV adoption data with total vehicle sales
        
    Returns:
        pandas.DataFrame: Data with market share calculated
    """
    if 'ev_sales' not in data.columns or 'total_sales' not in data.columns:
        return data  # Return original data if required columns are missing
    
    processed_data = data.copy()
    
    # Calculate market share as percentage
    processed_data['market_share'] = (processed_data['ev_sales'] / processed_data['total_sales']) * 100
    
    return processed_data

def get_top_regions(data, year, metric='sales', n=5):
    """
    Identifies the top regions based on a specified metric for a given year.
    
    Args:
        data (pandas.DataFrame): Cleaned EV adoption data
        year (int): Year to analyze
        metric (str): Metric to use for ranking (e.g., 'sales', 'market_share')
        n (int): Number of top regions to return
        
    Returns:
        pandas.DataFrame: Top regions data
    """
    if year not in data['year'].unique() or metric not in data.columns:
        return pd.DataFrame()  # Return empty DataFrame if year or metric is invalid
    
    year_data = data[data['year'] == year]
    
    # Group by region and sum the metric
    region_data = year_data.groupby('region')[metric].sum().reset_index()
    
    # Sort and get top n regions
    top_regions = region_data.sort_values(metric, ascending=False).head(n)
    
    return top_regions
