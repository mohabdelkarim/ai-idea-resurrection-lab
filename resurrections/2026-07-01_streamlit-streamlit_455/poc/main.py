import streamlit as st
import pandas as pd
import numpy as np
from streamlit.js_v1 import eval_script

# Create a sample dataframe
st.title("Interactive Dataframe")
df = pd.DataFrame({
    "Column1": [1, 2, 3, 4, 5],
    "Column2": [6, 7, 8, 9, 10]
})

# Function to handle user interactions
def handle_interaction():
    try:
        # Get the clicked row index
        clicked_row = st.session_state.get("clicked_row")
        if clicked_row is not None:
            st.write(f"You clicked on row: {clicked_row}")
            # Perform some action based on the clicked row
            st.session_state.clicked_row = None
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Display the dataframe
st.dataframe(df)

# Add a button to simulate a click event
if st.button("Click on a row"):
    # For demonstration purposes, simulate a click on the first row
    st.session_state.clicked_row = 0

# Run the event handler
handle_interaction()

# Create a sample chart
st.title("Interactive Chart")
fig = st.pyplot({
    "x": [1, 2, 3, 4, 5],
    "y": [6, 7, 8, 9, 10]
})

# Function to handle chart interactions
def handle_chart_interaction():
    try:
        # Get the chart click event
        click_event = st.session_state.get("chart_click_event")
        if click_event is not None:
            st.write(f"You clicked on the chart at: {click_event}")
            # Perform some action based on the chart click event
            st.session_state.chart_click_event = None
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Run the chart event handler
handle_chart_interaction()

# Use eval_script to handle JavaScript events
def handle_js_event():
    try:
        js_event = eval_script("get_chart_click_event()")
        if js_event is not None:
            st.session_state.chart_click_event = js_event
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Run the JavaScript event handler
handle_js_event()