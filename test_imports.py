import streamlit
import pandas
import numpy
import plotly.express
import plotly.graph_objects
import plotly.figure_factory

# Test core app imports
try:
    from utils.data_loader import load_sample_data
    print("✓ Successfully imported load_sample_data")
except Exception as e:
    print(f"× Error importing load_sample_data: {e}")

try:
    from utils.data_processor import clean_data, calculate_growth_rates, calculate_market_share
    print("✓ Successfully imported data_processor functions")
except Exception as e:
    print(f"× Error importing data_processor functions: {e}")

try:
    from utils.data_visualizer import plot_global_trends, create_choropleth_map
    print("✓ Successfully imported data_visualizer functions")
except Exception as e:
    print(f"× Error importing data_visualizer functions: {e}")

try:
    from utils.forecasting import forecast_linear, forecast_polynomial, plot_forecast
    print("✓ Successfully imported forecasting functions")
except Exception as e:
    print(f"× Error importing forecasting functions: {e}")

# Test page imports
try:
    import pages.overview
    print("✓ Successfully imported pages.overview")
except Exception as e:
    print(f"× Error importing pages.overview: {e}")

try:
    import pages.regional_analysis
    print("✓ Successfully imported pages.regional_analysis")
except Exception as e:
    print(f"× Error importing pages.regional_analysis: {e}")

try:
    import pages.market_share
    print("✓ Successfully imported pages.market_share")
except Exception as e:
    print(f"× Error importing pages.market_share: {e}")

try:
    import pages.forecasting
    print("✓ Successfully imported pages.forecasting")
except Exception as e:
    print(f"× Error importing pages.forecasting: {e}")

# Test sample data generation
try:
    from assets.sample_data import generate_sample_data
    print("✓ Successfully imported generate_sample_data")
except Exception as e:
    print(f"× Error importing generate_sample_data: {e}")