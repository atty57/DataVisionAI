# EV Adoption Analysis Dashboard

[Dashboard Preview](![EV adoption analysis](https://github.com/user-attachments/assets/ba8fd782-7347-4a58-8655-a7fb58894ea1)


A comprehensive interactive dashboard for analyzing global Electric Vehicle (EV) adoption trends built with Streamlit and PostgreSQL. The dashboard provides deep insights into EV market trends through advanced data visualization and predictive analytics.

## Features

- **Multi-page Interactive Dashboard**: Navigate through different analytical views of EV adoption data
- **Data Visualization**: Explore trends with dynamic charts and maps
- **Forecasting**: Predict future EV adoption rates using machine learning models
- **Data Upload**: Upload and analyze your own EV adoption datasets
- **Persistent Storage**: PostgreSQL database integration for efficient data management
- **Regional Analysis**: Compare EV adoption across different regions and countries
- **Market Share Analysis**: Track EV market penetration over time
- **User-friendly Interface**: Modern UI with interactive filters and data loading animations
- **Enhanced UX**: Progress bars and step-by-step loading indicators for improved user experience
- **Data Previews**: Automatic preview of uploaded data with real-time validation

## Technologies Used

- **Streamlit**: For the interactive web application framework
- **PostgreSQL**: Database for persistent data storage
- **SQLAlchemy**: ORM for database interactions
- **Pandas/NumPy**: For data manipulation and analysis
- **Plotly/Matplotlib/Seaborn**: For interactive data visualizations
- **Scikit-learn**: For forecasting models

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL database

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ev-adoption-dashboard.git
   cd ev-adoption-dashboard
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install required packages
   pip install streamlit>=1.22.0 pandas>=1.5.0 numpy>=1.23.0 plotly>=5.13.0 
   pip install matplotlib>=3.7.0 seaborn>=0.12.0 scikit-learn>=1.2.0
   pip install sqlalchemy>=2.0.0 psycopg2-binary>=2.9.5 python-dotenv>=1.0.0
   ```

3. Set up your PostgreSQL database and configure connection:
   - Create a new PostgreSQL database
   - Set the following environment variables or create a `.env` file:
     ```
     DATABASE_URL=postgresql://username:password@localhost:5432/ev_adoption_db
     ```

4. Initialize the database:
   ```bash
   python -c "from utils.database import init_db; init_db()"
   ```

## Usage

1. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and navigate to `http://localhost:8501`

3. Use the sidebar to:
   - Select data source (sample data or upload your own CSV)
   - Filter by year range and regions
   - Navigate between different analysis pages

## Data Requirements

If you're uploading your own data, the CSV file should include the following columns:
- `year`: The year of the data point
- `region`: The region or country name
- `sales`: EV sales numbers
- `market_share` (optional): EV market share as percentage
- `ev_type` (optional): Type of EV (BEV, PHEV, etc.)
- `total_vehicle_sales` (optional): Total vehicle sales for market share calculation

## Project Structure

```
ev-adoption-dashboard/
├── app.py                    # Main application entry point
├── pages/                    # Dashboard page modules
│   ├── overview.py           # Overview page
│   ├── regional_analysis.py  # Regional comparison page
│   ├── market_share.py       # Market share analysis page
│   └── forecasting.py        # Forecasting page
├── utils/                    # Utility modules
│   ├── data_loader.py        # Data loading functions
│   ├── data_processor.py     # Data processing functions
│   ├── data_visualizer.py    # Visualization functions
│   ├── database.py           # Database interaction
│   └── forecasting.py        # Forecasting models
└── assets/                   # Static assets
    └── sample_data.py        # Sample data generator
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Data sources: [provide sources if applicable]
- Special thanks to contributors and the open-source community

---

## Screenshots

### Overview Page
![Overview Page](assets/overview_page.png)

### Regional Analysis
![Regional Analysis](assets/regional_analysis.png)

### Market Share Analysis
![Market Share](assets/market_share.png)

### Forecasting
![Forecasting](assets/forecasting.png)
