import pandas as pd
import numpy as np
from assets.sample_data import generate_sample_data

def load_sample_data():
    """
    Loads sample EV adoption data for demonstration purposes.
    In a real application, this would load from an external source.
    
    Returns:
        pandas.DataFrame: Sample EV adoption data
    """
    return generate_sample_data()

def load_data_from_csv(file_path):
    """
    Loads EV adoption data from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: EV adoption data
    """
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        raise ValueError(f"Error loading data from {file_path}: {e}")
