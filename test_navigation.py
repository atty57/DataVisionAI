import streamlit as st
import pandas as pd
import numpy as np

# Set page title
st.title("Navigation Test App")

# Initialize session state for page
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# Create dummy data for session state
if 'test_data' not in st.session_state:
    st.session_state.test_data = pd.DataFrame({
        'year': range(2010, 2024),
        'sales': np.random.randint(1000, 100000, 14)
    })
    st.session_state.cleaned_data = st.session_state.test_data

# Function to show home page
def show_home():
    st.header("Home Page")
    st.write("This is the home page. Use the sidebar to navigate to other pages.")
    
    # Display the test data
    st.dataframe(st.session_state.test_data)

# Function to show page 1
def show_page1():
    st.header("Page 1")
    st.write("This is Page 1. This tests if we can navigate between pages.")
    
    if st.button("Show test data"):
        st.dataframe(st.session_state.cleaned_data)

# Function to show page 2
def show_page2():
    st.header("Page 2")
    st.write("This is Page 2. Let's see if session state is preserved.")
    
    # Add a widget that updates session state
    new_value = st.slider("Update a value", 0, 100, 50)
    if st.button("Update session state"):
        st.session_state.test_value = new_value
        st.success(f"Updated session state with value: {new_value}")
    
    # Display the value if it exists
    if 'test_value' in st.session_state:
        st.write(f"Current value in session state: {st.session_state.test_value}")

# Sidebar for navigation
st.sidebar.title("Navigation Test")
page = st.sidebar.radio(
    "Select Page",
    ["Home", "Page 1", "Page 2"]
)

# Update session state
st.session_state.current_page = page

# Display the selected page
if page == "Home":
    show_home()
elif page == "Page 1":
    show_page1()
elif page == "Page 2":
    show_page2()

# Show current session state (for debugging)
st.sidebar.header("Session State Debug")
if st.sidebar.checkbox("Show session state"):
    st.sidebar.write(st.session_state)