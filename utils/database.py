import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Float, String, MetaData, Table, select, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# Get database credentials from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

# Handle case when DATABASE_URL is not set
if not DATABASE_URL:
    print("Warning: DATABASE_URL environment variable not set. Using SQLite database instead.")
    DATABASE_URL = 'sqlite:///ev_data.db'

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create base class for declarative models
Base = declarative_base()

# Define EV data model
class EVData(Base):
    __tablename__ = 'ev_data'
    
    id = Column(Integer, primary_key=True)
    year = Column(Integer, index=True)
    region = Column(String, index=True)
    sales = Column(Float)
    market_share = Column(Float, nullable=True)
    growth_rate = Column(Float, nullable=True)
    ev_type = Column(String, nullable=True)
    total_vehicle_sales = Column(Float, nullable=True)
    
    def __repr__(self):
        return f"<EVData(region='{self.region}', year={self.year}, sales={self.sales})>"

# Initialize database
def init_db():
    Base.metadata.create_all(engine)
    print("Database tables created.")

# Create a session factory
Session = sessionmaker(bind=engine)

# Function to save data to the database
def save_data_to_db(data_df):
    """
    Save pandas DataFrame to database
    
    Args:
        data_df (pandas.DataFrame): DataFrame containing EV data
    """
    session = Session()
    
    try:
        # Convert DataFrame rows to model instances
        data_records = []
        for _, row in data_df.iterrows():
            record = EVData(
                year=int(row['year']),
                region=row['region'],
                sales=float(row['sales']),
                market_share=float(row['market_share']) if 'market_share' in row and pd.notna(row['market_share']) else None,
                growth_rate=float(row['growth_rate']) if 'growth_rate' in row and pd.notna(row['growth_rate']) else None,
                ev_type=row['ev_type'] if 'ev_type' in row and pd.notna(row['ev_type']) else None,
                total_vehicle_sales=float(row['total_vehicle_sales']) if 'total_vehicle_sales' in row and pd.notna(row['total_vehicle_sales']) else None
            )
            data_records.append(record)
        
        # Add all records
        session.add_all(data_records)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error saving data to database: {e}")
        return False
    finally:
        session.close()

# Function to load data from the database
def load_data_from_db():
    """
    Load EV data from database
    
    Returns:
        pandas.DataFrame: DataFrame containing EV data
    """
    session = Session()
    
    try:
        # Query all data
        result = session.query(EVData).all()
        
        # Convert to DataFrame
        data = []
        for record in result:
            row = {
                'year': record.year,
                'region': record.region,
                'sales': record.sales
            }
            
            # Add optional columns if they exist
            if record.market_share is not None:
                row['market_share'] = record.market_share
            
            if record.growth_rate is not None:
                row['growth_rate'] = record.growth_rate
                
            if record.ev_type is not None:
                row['ev_type'] = record.ev_type
                
            if record.total_vehicle_sales is not None:
                row['total_vehicle_sales'] = record.total_vehicle_sales
            
            data.append(row)
        
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error loading data from database: {e}")
        return pd.DataFrame()
    finally:
        session.close()

# Function to filter data by criteria
def filter_data_from_db(min_year=None, max_year=None, regions=None):
    """
    Load filtered EV data from database
    
    Args:
        min_year (int, optional): Minimum year to include
        max_year (int, optional): Maximum year to include
        regions (list, optional): List of regions to include
        
    Returns:
        pandas.DataFrame: DataFrame containing filtered EV data
    """
    session = Session()
    
    try:
        # Start with base query
        query = session.query(EVData)
        
        # Apply filters
        if min_year is not None:
            query = query.filter(EVData.year >= min_year)
            
        if max_year is not None:
            query = query.filter(EVData.year <= max_year)
            
        if regions is not None and len(regions) > 0:
            query = query.filter(EVData.region.in_(regions))
        
        # Execute query
        result = query.all()
        
        # Convert to DataFrame
        data = []
        for record in result:
            row = {
                'year': record.year,
                'region': record.region,
                'sales': record.sales
            }
            
            # Add optional columns if they exist
            if record.market_share is not None:
                row['market_share'] = record.market_share
            
            if record.growth_rate is not None:
                row['growth_rate'] = record.growth_rate
                
            if record.ev_type is not None:
                row['ev_type'] = record.ev_type
                
            if record.total_vehicle_sales is not None:
                row['total_vehicle_sales'] = record.total_vehicle_sales
            
            data.append(row)
        
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error loading filtered data from database: {e}")
        return pd.DataFrame()
    finally:
        session.close()

# Function to check if database has data
def db_has_data():
    """
    Check if the database contains any EV data
    
    Returns:
        bool: True if data exists, False otherwise
    """
    session = Session()
    
    try:
        count = session.query(func.count(EVData.id)).scalar()
        return count > 0
    except Exception as e:
        print(f"Error checking database data: {e}")
        return False
    finally:
        session.close()

# Function to clear all data
def clear_db_data():
    """
    Remove all data from the database
    
    Returns:
        bool: True if successful, False otherwise
    """
    session = Session()
    
    try:
        session.query(EVData).delete()
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error clearing database: {e}")
        return False
    finally:
        session.close()

# Function to get unique regions and years
def get_db_metadata():
    """
    Get metadata about the database contents
    
    Returns:
        tuple: (regions, years) - lists of unique regions and years
    """
    session = Session()
    
    try:
        regions = [r[0] for r in session.query(EVData.region).distinct()]
        years = [y[0] for y in session.query(EVData.year).distinct().order_by(EVData.year)]
        return regions, years
    except Exception as e:
        print(f"Error retrieving database metadata: {e}")
        return [], []
    finally:
        session.close()