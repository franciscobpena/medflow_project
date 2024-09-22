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
PAGE_TITLE = "Marketplace - Customer View"
PAGE_ICON = "📊"
SIDEBAR_HEADER = 'Indian Food Delivery Company'
SIDEBAR_SUBHEADER = 'Fastest Delivery in Town'
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


def plot_order_by_day(df_filtered):
    """Plots the number of orders per day."""
    order_day_quantity = df_filtered.groupby('Order_Date')['ID'].count().reset_index()
    fig = px.bar(order_day_quantity, x='Order_Date', y='ID',
                 labels={'Order_Date': 'Order Date', 'ID': 'Number of Orders'})
    st.plotly_chart(fig, use_container_width=True)


def plot_order_by_traffic(df_filtered):
    """Plots the number of orders by traffic density."""
    order_traffic_density = df_filtered.groupby(['Road_traffic_density', 'Order_Date'])['ID'].nunique().reset_index()
    fig = px.box(order_traffic_density, x='Road_traffic_density', y='ID',
                 labels={'Road_traffic_density': 'Traffic Density', 'ID': 'Number of Unique Orders'})
    st.plotly_chart(fig)


def plot_traffic_by_city(df_filtered):
    """Plots the traffic orders by city."""
    df_cleaned = df_filtered.dropna(subset=['City', 'Road_traffic_density'])
    df_grouped = df_cleaned.groupby(['City', 'Road_traffic_density'])['ID'].count().reset_index()
    fig = px.scatter(df_grouped, x='City', y='Road_traffic_density', size='ID', color='City',
                     labels={'City': 'City', 'Road_traffic_density': 'Traffic Density'})
    st.plotly_chart(fig, use_container_width=True)


def plot_age_distribution_by_city(df_filtered):
    """Plots the age distribution of delivery persons by city."""
    fig = px.box(df_filtered, x='City', y='Delivery_person_Age',
                 labels={'Delivery_person_Age': 'Age', 'City': 'City'})
    st.plotly_chart(fig, use_container_width=True)


def order_metric(df, period='day'):
    """Plots the orders metric by day or week."""
    if period == 'day':
        st.header('Orders by Day')
        df_aux = df.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
        df_aux.columns = ['order_date', 'total_orders']
        fig = px.bar(df_aux, x='order_date', y='total_orders',
                     labels={'order_date': 'Order Date', 'total_orders': 'Total Orders'})
    else:
        st.header('Orders by Week')
        df_aux = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        fig = px.bar(df_aux, x='week_of_year', y='ID',
                     labels={'week_of_year': 'Week of the Year', 'ID': 'Total Orders'})

    st.plotly_chart(fig, use_container_width=True)


def plot_orders_analysis_by_week(df):
    """Plots the total number of orders per week and orders per deliverer per week."""
    df['week_of_year'] = df['Order_Date'].dt.strftime("%U")
    weekly_stats = df.groupby('week_of_year').agg(
        total_orders=('ID', 'count'),
        unique_deliverers=('Delivery_person_ID', 'nunique')
    ).reset_index()
    weekly_stats['orders_per_deliverer'] = weekly_stats['total_orders'] / weekly_stats['unique_deliverers']

    fig1 = px.bar(weekly_stats, x='week_of_year', y='total_orders',
                  labels={'week_of_year': 'Week of the Year', 'total_orders': 'Total Orders'})
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.line(weekly_stats, x='week_of_year', y='orders_per_deliverer',
                   labels={'week_of_year': 'Week of the Year', 'orders_per_deliverer': 'Orders per Deliverer'})
    st.plotly_chart(fig2)


def plot_density_map(df_filtered):
    """Plots the traffic density on a map."""
    central_locations = df_filtered.groupby(['City', 'Road_traffic_density']).agg({
        'Delivery_location_latitude': 'median',
        'Delivery_location_longitude': 'median'
    }).reset_index()
    map_center = [central_locations['Delivery_location_latitude'].mean(), central_locations['Delivery_location_longitude'].mean()]
    mymap = folium.Map(location=map_center, zoom_start=5)
    for _, location_info in central_locations.iterrows():
        folium.Marker(
            location=[location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']],
            popup=f"{location_info['City']} - {location_info['Road_traffic_density']}",
        ).add_to(mymap)
    folium_static(mymap, width=900, height=600)


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

# ===========================
# STREAMLIT LAYOUT
# ===========================
# Create tabs with icons
tab1, tab2, tab3 = st.tabs(['📊 Management View', '📝 Tactical View', '🌍 Geographical View'])

with tab1:
    with st.container():
        plot_order_by_day(df_filtered)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            plot_order_by_traffic(df_filtered)
        with col2:
            plot_traffic_by_city(df_filtered)
    with st.container():
        plot_age_distribution_by_city(df_filtered)

with tab2:
    st.markdown("# Orders Analysis by Week")
    plot_orders_analysis_by_week(df_filtered)

with tab3:
    st.markdown("# Country Maps")
    plot_density_map(df_filtered)
