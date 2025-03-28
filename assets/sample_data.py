import pandas as pd
import numpy as np

def generate_sample_data():
    """
    Generates realistic sample data for EV adoption based on real-world trends.
    This is used when no external data is provided.
    
    Returns:
        pandas.DataFrame: Sample EV adoption data
    """
    # Base years for the dataset
    years = list(range(2010, 2024))
    
    # Define regions with different adoption patterns
    regions = [
        'China', 'Europe', 'United States', 'Norway', 'Germany', 
        'France', 'United Kingdom', 'Japan', 'South Korea', 'Canada'
    ]
    
    # Generate data structure
    data_records = []
    
    # Different growth patterns for different regions
    growth_patterns = {
        'China': {'base': 5000, 'growth': 1.65, 'acceleration': 0.15, 'market_share_base': 0.1, 'market_share_growth': 0.5},
        'Europe': {'base': 8000, 'growth': 1.55, 'acceleration': 0.12, 'market_share_base': 0.2, 'market_share_growth': 0.45},
        'United States': {'base': 4000, 'growth': 1.45, 'acceleration': 0.08, 'market_share_base': 0.1, 'market_share_growth': 0.35},
        'Norway': {'base': 1000, 'growth': 1.70, 'acceleration': 0.20, 'market_share_base': 1.0, 'market_share_growth': 0.70},
        'Germany': {'base': 2000, 'growth': 1.60, 'acceleration': 0.14, 'market_share_base': 0.3, 'market_share_growth': 0.50},
        'France': {'base': 1500, 'growth': 1.58, 'acceleration': 0.13, 'market_share_base': 0.2, 'market_share_growth': 0.48},
        'United Kingdom': {'base': 1800, 'growth': 1.57, 'acceleration': 0.12, 'market_share_base': 0.25, 'market_share_growth': 0.47},
        'Japan': {'base': 1200, 'growth': 1.40, 'acceleration': 0.07, 'market_share_base': 0.15, 'market_share_growth': 0.30},
        'South Korea': {'base': 900, 'growth': 1.50, 'acceleration': 0.10, 'market_share_base': 0.12, 'market_share_growth': 0.40},
        'Canada': {'base': 800, 'growth': 1.48, 'acceleration': 0.09, 'market_share_base': 0.1, 'market_share_growth': 0.38}
    }
    
    # Generate EV sales data with realistic growth patterns
    for region in regions:
        pattern = growth_patterns.get(region, {'base': 1000, 'growth': 1.5, 'acceleration': 0.1, 
                                               'market_share_base': 0.1, 'market_share_growth': 0.4})
        base = pattern['base']
        growth_factor = pattern['growth']
        acceleration = pattern['acceleration']
        market_share_base = pattern['market_share_base']
        market_share_growth = pattern['market_share_growth']
        
        for year in years:
            # Calculate years since start
            years_since_start = year - 2010
            
            # Simulate exponential growth with acceleration
            growth_multiplier = growth_factor ** (years_since_start * (1 + acceleration * years_since_start / 10))
            sales = int(base * growth_multiplier)
            
            # Add some noise for realism
            sales = int(sales * np.random.normal(1, 0.1))
            
            # Ensure minimum sales
            sales = max(10, sales)
            
            # Generate realistic market share
            # Market share grows with a logistic pattern, starting slow, accelerating, then slowing as it approaches limits
            years_factor = years_since_start / 10  # Normalize to 0-1 range over decade
            market_share = market_share_base * (1 + market_share_growth) ** years_factor
            
            # Add noise to market share
            market_share = market_share * np.random.normal(1, 0.05)
            
            # Cap market share at 100%
            market_share = min(100, market_share)
            
            # Create data record
            record = {
                'year': year,
                'region': region,
                'sales': sales,
                'market_share': market_share
            }
            
            data_records.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(data_records)
    
    # Add vehicle type data for a subset of the records
    df['vehicle_type'] = np.random.choice(['BEV', 'PHEV'], size=len(df), p=[0.7, 0.3])
    
    # Generate vehicle segment data
    segments = ['Sedan', 'SUV', 'Hatchback', 'Truck', 'Van']
    df['vehicle_segment'] = np.random.choice(segments, size=len(df), p=[0.3, 0.4, 0.15, 0.1, 0.05])
    
    # Ensure data types
    df['year'] = df['year'].astype(int)
    df['sales'] = df['sales'].astype(int)
    df['market_share'] = df['market_share'].astype(float)
    
    return df
