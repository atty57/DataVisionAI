import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error, r2_score

def forecast_linear(data, time_col='year', target_col='sales', periods=5):
    """
    Performs simple linear regression forecasting for time series data.
    
    Args:
        data (pandas.DataFrame): Time series data to forecast
        time_col (str): Column name for time periods
        target_col (str): Column name for the target variable to forecast
        periods (int): Number of periods to forecast into the future
        
    Returns:
        tuple: (forecast_df, model_metrics, model)
            - forecast_df: DataFrame with historical and forecasted values
            - model_metrics: Dictionary with model performance metrics
            - model: The fitted model object
    """
    if time_col not in data.columns or target_col not in data.columns or len(data) < 3:
        return pd.DataFrame(), {'error': 'Insufficient data for forecasting'}, None
    
    # Aggregate data by time period
    time_series = data.groupby(time_col)[target_col].sum().reset_index()
    time_series = time_series.sort_values(time_col)
    
    # Prepare data for modeling
    X = time_series[time_col].values.reshape(-1, 1)
    y = time_series[target_col].values
    
    # Train linear regression model
    model = LinearRegression()
    model.fit(X, y)
    
    # Calculate metrics on training data
    y_pred = model.predict(X)
    mse = mean_squared_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    
    # Generate forecast periods
    last_period = time_series[time_col].max()
    future_periods = np.array(range(last_period + 1, last_period + periods + 1)).reshape(-1, 1)
    
    # Make predictions
    future_predictions = model.predict(future_periods)
    
    # Create forecast DataFrame
    historical = pd.DataFrame({
        time_col: time_series[time_col],
        target_col: time_series[target_col],
        'type': 'historical'
    })
    
    future = pd.DataFrame({
        time_col: future_periods.flatten(),
        target_col: future_predictions,
        'type': 'forecast'
    })
    
    forecast_df = pd.concat([historical, future], ignore_index=True)
    
    # Model metrics
    model_metrics = {
        'mse': mse,
        'rmse': np.sqrt(mse),
        'r2': r2,
        'coefficient': model.coef_[0],
        'intercept': model.intercept_
    }
    
    return forecast_df, model_metrics, model

def forecast_polynomial(data, time_col='year', target_col='sales', periods=5, degree=2):
    """
    Performs polynomial regression forecasting for time series data.
    
    Args:
        data (pandas.DataFrame): Time series data to forecast
        time_col (str): Column name for time periods
        target_col (str): Column name for the target variable to forecast
        periods (int): Number of periods to forecast into the future
        degree (int): Degree of the polynomial function
        
    Returns:
        tuple: (forecast_df, model_metrics, model)
            - forecast_df: DataFrame with historical and forecasted values
            - model_metrics: Dictionary with model performance metrics
            - model: The fitted model object
    """
    if time_col not in data.columns or target_col not in data.columns or len(data) < degree + 1:
        return pd.DataFrame(), {'error': 'Insufficient data for polynomial forecasting'}, None
    
    # Aggregate data by time period
    time_series = data.groupby(time_col)[target_col].sum().reset_index()
    time_series = time_series.sort_values(time_col)
    
    # Prepare data for modeling
    X = time_series[time_col].values.reshape(-1, 1)
    y = time_series[target_col].values
    
    # Create polynomial features and model
    model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
    model.fit(X, y)
    
    # Calculate metrics on training data
    y_pred = model.predict(X)
    mse = mean_squared_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    
    # Generate forecast periods
    last_period = time_series[time_col].max()
    future_periods = np.array(range(last_period + 1, last_period + periods + 1)).reshape(-1, 1)
    
    # Make predictions
    future_predictions = model.predict(future_periods)
    
    # Create forecast DataFrame
    historical = pd.DataFrame({
        time_col: time_series[time_col],
        target_col: time_series[target_col],
        'type': 'historical'
    })
    
    future = pd.DataFrame({
        time_col: future_periods.flatten(),
        target_col: future_predictions,
        'type': 'forecast'
    })
    
    forecast_df = pd.concat([historical, future], ignore_index=True)
    
    # Model metrics
    model_metrics = {
        'mse': mse,
        'rmse': np.sqrt(mse),
        'r2': r2,
        'degree': degree
    }
    
    return forecast_df, model_metrics, model

def forecast_by_region(data, region_col='region', time_col='year', target_col='sales', periods=5, method='linear'):
    """
    Performs forecasting for multiple regions.
    
    Args:
        data (pandas.DataFrame): Time series data to forecast
        region_col (str): Column name for regions
        time_col (str): Column name for time periods
        target_col (str): Column name for the target variable to forecast
        periods (int): Number of periods to forecast into the future
        method (str): Forecasting method ('linear' or 'polynomial')
        
    Returns:
        pandas.DataFrame: Forecasted values for all regions
    """
    if region_col not in data.columns or time_col not in data.columns or target_col not in data.columns:
        return pd.DataFrame()
    
    regions = data[region_col].unique()
    all_forecasts = []
    
    for region in regions:
        region_data = data[data[region_col] == region]
        
        if len(region_data) < 3:
            continue  # Skip regions with insufficient data
        
        if method == 'polynomial':
            forecast_df, _, _ = forecast_polynomial(region_data, time_col, target_col, periods)
        else:
            forecast_df, _, _ = forecast_linear(region_data, time_col, target_col, periods)
        
        if not forecast_df.empty:
            forecast_df[region_col] = region
            all_forecasts.append(forecast_df)
    
    if all_forecasts:
        return pd.concat(all_forecasts, ignore_index=True)
    else:
        return pd.DataFrame()

def plot_forecast(forecast_df, time_col='year', target_col='sales', title=''):
    """
    Creates a visualization of forecasted values.
    
    Args:
        forecast_df (pandas.DataFrame): DataFrame with historical and forecasted values
        time_col (str): Column name for time periods
        target_col (str): Column name for the target variable
        title (str): Title for the plot
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    if forecast_df.empty or 'type' not in forecast_df.columns:
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for forecast visualization",
            showarrow=False,
            font=dict(size=14)
        )
        return fig
    
    import plotly.express as px
    
    # Create separate traces for historical and forecast data
    historical = forecast_df[forecast_df['type'] == 'historical']
    forecast = forecast_df[forecast_df['type'] == 'forecast']
    
    fig = px.line(
        forecast_df, 
        x=time_col, 
        y=target_col,
        color='type',
        labels={target_col: target_col.capitalize(), time_col: time_col.capitalize()},
        title=title or f'Forecast of {target_col.capitalize()} Over Time',
        color_discrete_map={'historical': 'blue', 'forecast': 'red'}
    )
    
    fig.update_layout(
        xaxis=dict(tickmode='linear'),
        hovermode='x unified'
    )
    
    return fig
