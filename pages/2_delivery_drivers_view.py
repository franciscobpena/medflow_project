# ===========================
# LIBRARIES
# ===========================
import pandas as pd
import numpy as np
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
from datetime import datetime
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import os

# ===========================
# CONSTANTS
# ===========================
FILE_PATH = os.path.join('dataset', 'train.csv')
IMAGE_PATH = 'logo.png'
PAGE_TITLE = "Marketplace - Delivery Drivers View"
PAGE_ICON = "📊"
SIDEBAR_HEADER = 'Indian Food Delivery Company'
POWERED_BY = '## Powered by Francisco Pena 🤓'
DATE_FORMAT = 'DD-MM-YYYY'

# ===========================
# FUNCTIONS
# ===========================

def clean_data(df):
    """Cleans and preprocesses the data."""
    # Remove whitespace from strings
    df['ID'] = df['ID'].str.strip()
    df['Delivery_person_ID'] = df['Delivery_person_ID'].str.strip()

    # Convert the 'Delivery_person_Age' column to numeric, converting invalid values (like 'NaN' string) to NaN
    df['Delivery_person_Age'] = pd.to_numeric(df['Delivery_person_Age'], errors='coerce')
    df = df.dropna(subset=['Delivery_person_Age'])  # Drop rows where 'Delivery_person_Age' contains NaN values after conversion
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)  # Convert the 'Delivery_person_Age' column to integer

    # Conversion of text/category/string to floating-point numbers
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)

    # Convert text to date
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')

    # Convert 'Time_Orderd' and 'Time_Order_picked' to datetime, focusing only on the time part
    df['Time_Orderd'] = pd.to_datetime(df['Time_Orderd'], errors='coerce')
    df['Time_Order_picked'] = pd.to_datetime(df['Time_Order_picked'], errors='coerce')

    # Process 'Time_taken(min)' column
    df['Time_taken(min)'] = df['Time_taken(min)'].str.replace('(min)', '', regex=False).str.strip()
    df['Time_taken(min)'] = pd.to_numeric(df['Time_taken(min)'], errors='coerce')

    # Remove rows with "NaN" strings
    nan_cols = ["Delivery_person_Age", "Delivery_person_Ratings", "Time_taken(min)", "Road_traffic_density", "multiple_deliveries", "Festival", "City"]
    for col in nan_cols:
        df = df[df[col] != "NaN "]

    # Standardize column values
    columns_to_standardize = ['ID', 'Road_traffic_density', 'Type_of_order', 'Type_of_vehicle', 'City']
    df[columns_to_standardize] = df[columns_to_standardize].apply(lambda x: x.str.strip().str.capitalize())

    return df


def apply_filters(df, date_slider, traffic_options):
    """Applies filters to the dataframe based on user input."""
    df_filtered = df[(df['Order_Date'] <= date_slider) & (df['Road_traffic_density'].isin(traffic_options))]
    return df_filtered


def calculate_metrics(df_filtered):
    """Calculates various metrics for delivery drivers."""
    older_age = df_filtered['Delivery_person_Age'].max()
    younger_age = df_filtered['Delivery_person_Age'].min()
    best_vehicle = df_filtered['Vehicle_condition'].max()
    worst_vehicle = df_filtered['Vehicle_condition'].min()
    df_avg_ratings_per_deliver = (
        df_filtered.groupby('Delivery_person_ID')['Delivery_person_Ratings']
        .mean()
        .reset_index()
    )
    return older_age, younger_age, best_vehicle, worst_vehicle, df_avg_ratings_per_deliver


def get_avg_rating_by_traffic(df):
    """Calculates average rating by traffic condition."""
    return df.groupby('Road_traffic_density')['Delivery_person_Ratings'].mean().reset_index()


def get_avg_rating_by_weather(df):
    """Calculates average rating by weather condition."""
    return df.groupby('Weatherconditions')['Delivery_person_Ratings'].mean().reset_index()


def plot_delivery_time_by_city(df_filtered):
    """Plots the delivery time distribution by city."""
    fig = px.box(df_filtered, x='City', y='Time_taken(min)',
                 labels={'City': 'City', 'Time_taken(min)': 'Time Taken (min)'})
    st.plotly_chart(fig, use_container_width=True)

# ===========================
# ETL PROCESS
# ===========================
# Data Extraction
df = pd.read_csv(FILE_PATH)

# Data Cleaning and Transformation
df = clean_data(df)

# Streamlit Layout and Sidebar
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout='wide')
st.header(PAGE_TITLE)

# Sidebar with Filters
try:
    image = Image.open(IMAGE_PATH)
    st.sidebar.image(image, width=120)
except FileNotFoundError:
    st.sidebar.error(f"Image not found at the path: {IMAGE_PATH}")

st.sidebar.markdown(f'#{SIDEBAR_HEADER}')
st.sidebar.markdown("""---""")

date_slider = st.sidebar.slider('Until what date?', value=datetime(2022, 4, 13),
                                min_value=datetime(2022, 2, 11), max_value=datetime(2022, 4, 13),
                                format=DATE_FORMAT)
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect('What are the traffic conditions?',
                                         ['Low', 'Medium', 'High', 'Jam'],
                                         default=['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""---""")
st.sidebar.markdown(POWERED_BY)

# Apply Filters
df_filtered = apply_filters(df, date_slider, traffic_options)

# Calculate Metrics
older_age, younger_age, best_vehicle, worst_vehicle, df_avg_ratings_per_deliver = calculate_metrics(df_filtered)

# ===========================
# STREAMLIT LAYOUT
# ===========================
tab1, tab2, tab3 = st.tabs(['📊 Management View', '-', '-'])

with tab1:
    with st.container():
        st.title("Overall Metrics")
        col1, col2, col3, col4 = st.columns(4, gap="small")
        
        col1.metric("Older Delivery Age", older_age)
        col2.metric("Younger Delivery Age", younger_age)
        col3.metric("Best Vehicle Condition", best_vehicle)
        col4.metric("Worst Vehicle Condition", worst_vehicle)

    with st.container():
        st.markdown("""---""")
        st.title("Ratings")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Average Ratings per Deliverer")
            st.dataframe(df_avg_ratings_per_deliver)

        with col2:
            st.subheader("Average Ratings by Traffic Condition")
            st.dataframe(get_avg_rating_by_traffic(df_filtered))

            st.subheader("Average Ratings by Weather Condition")
            st.dataframe(get_avg_rating_by_weather(df_filtered))

    with st.container():
        st.markdown("""---""")
        st.title('Speed of Delivery')
        plot_delivery_time_by_city(df_filtered)

