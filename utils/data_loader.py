import pandas as pd
import numpy as np
from assets.sample_data import generate_sample_data
from utils.database import load_data_from_db, db_has_data, save_data_to_db, clear_db_data, get_db_metadata, init_db, filter_data_from_db

def load_sample_data():
    """
    Loads sample EV adoption data for demonstration purposes.
    Checks if data exists in database first. If not, loads sample data
    and stores it in the database.
    
    Returns:
        pandas.DataFrame: Sample EV adoption data
    """
    # Check if database has been initialized
    try:
        init_db()
    except Exception as e:
        print(f"Error initializing database: {e}")
    
    # Check if data exists in database
    if db_has_data():
        print("Loading sample data from database")
        return load_data_from_db()
    else:
        print("Generating sample data and saving to database")
        # Generate sample data
        sample_data = generate_sample_data()
        
        # Save to database
        save_data_to_db(sample_data)
        
        return sample_data

def load_data_from_csv(file_path):
    """
    Loads EV adoption data from a CSV file and stores it in the database.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: EV adoption data
    """
    try:
        # Load the CSV file
        data = pd.read_csv(file_path)
        
        # Initialize database if needed
        init_db()
        
        # Clear existing data
        clear_db_data()
        
        # Save to database
        save_data_to_db(data)
        
        return data
    except Exception as e:
        raise ValueError(f"Error loading data from {file_path}: {e}")

def get_data_metadata():
    """
    Retrieves metadata about the available data.
    
    Returns:
        tuple: (regions, years) - lists of unique regions and years
    """
    return get_db_metadata()

def load_filtered_data(min_year=None, max_year=None, regions=None):
    """
    Loads filtered data from the database.
    
    Args:
        min_year (int, optional): Minimum year to include
        max_year (int, optional): Maximum year to include
        regions (list, optional): List of regions to include
        
    Returns:
        pandas.DataFrame: Filtered EV adoption data
    """
    return filter_data_from_db(min_year, max_year, regions)
