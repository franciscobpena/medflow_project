# ===========================
# LIBRARIES
# ===========================
import pandas as pd
import numpy as np
from haversine import haversine, Unit
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
# Usando os.path.join para construir o caminho do arquivo, garantindo portabilidade
FILE_PATH = os.path.join('dataset', 'train.csv')
IMAGE_PATH = 'logo.png'
PAGE_TITLE = "Marketplace - Restaurant View"
PAGE_ICON = "📊"
CITY_COLUMN = 'City'
TIME_COLUMN = 'Time_taken(min)'
TRAFFIC_COLUMN = 'Road_traffic_density'
FESTIVAL_COLUMN = 'Festival'
ORDER_DATE_COLUMN = 'Order_Date'

# ===========================
# DATA PROCESSING FUNCTIONS
# ===========================

def clean_data(df):
    """
    Perform data cleaning tasks including removing whitespace, handling NaN values, and converting data types.

    Parameters:
    df (DataFrame): The original dataset.

    Returns:
    DataFrame: The cleaned dataset.
    """
    # Remove whitespace from strings and standardize
    string_columns = ['ID', 'Delivery_person_ID', CITY_COLUMN, TRAFFIC_COLUMN, 
                      'Type_of_order', 'Type_of_vehicle', FESTIVAL_COLUMN]
    df[string_columns] = df[string_columns].apply(lambda x: x.str.strip().str.capitalize())

    # Handle NaN values and conversions
    df = df[df['Delivery_person_Age'] != 'NaN '].copy()
    df['Delivery_person_Age'] = pd.to_numeric(df['Delivery_person_Age'], errors='coerce').dropna().astype(int)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    df[ORDER_DATE_COLUMN] = pd.to_datetime(df[ORDER_DATE_COLUMN], format='%d-%m-%Y')
    df[TIME_COLUMN] = df[TIME_COLUMN].str.replace('(min)', '', regex=False).str.strip().astype(int)
    df[FESTIVAL_COLUMN] = df[FESTIVAL_COLUMN].str.strip()

    return df

def calculate_distance(row):
    """
    Calculate the distance between the restaurant and the delivery location using the haversine formula.

    Parameters:
    row (Series): A row of the DataFrame.

    Returns:
    float: The distance in kilometers.
    """
    coord1 = (row['Restaurant_latitude'], row['Restaurant_longitude'])
    coord2 = (row['Delivery_location_latitude'], row['Delivery_location_longitude'])
    return haversine(coord1, coord2, unit=Unit.KILOMETERS)

# ===========================
# STREAMLIT CONFIGURATION
# ===========================

def configure_sidebar():
    """
    Configure the sidebar with the image, date slider, and traffic/festival options.
    """
    st.sidebar.markdown('# Indian Food Delivery Company')
    st.sidebar.markdown("""---""")

    # Load and display the image in the sidebar
    try:
        image = Image.open(IMAGE_PATH)
        st.sidebar.image(image, width=120)
    except FileNotFoundError:
        st.sidebar.error(f"Image not found at the path: {IMAGE_PATH}")
    
    # Date slider
    date_slider = st.sidebar.slider(
        'Until what date?',
        value=datetime(2022, 4, 13),
        min_value=datetime(2022, 2, 11),
        max_value=datetime(2022, 4, 13),
        format='DD-MM-YYYY'
    )

    st.sidebar.markdown("""---""")

    # Multiselect for traffic conditions
    traffic_options = st.sidebar.multiselect(
        'What are the traffic conditions?',
        ['Low', 'Medium', 'High', 'Jam'],
        default=['Low', 'Medium', 'High', 'Jam']
    )
    
    st.sidebar.markdown("""---""")

    # Multiselect for festivals
    festival_options = st.sidebar.multiselect(
        'Festivals',
        ['Yes', 'No'],
        default=['Yes', 'No']
    )
    
    st.sidebar.markdown("""---""")
    st.sidebar.markdown('## Powered by Francisco Pena 🤓')

    return date_slider, traffic_options, festival_options

# ===========================
# METRIC FUNCTIONS
# ===========================

def display_overall_metrics(df_filtered):
    """
    Display overall metrics such as unique delivery count, average distance, average delivery time, and standard deviation.
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        unique_delivery = df_filtered['Delivery_person_ID'].nunique()
        col1.metric("Unique delivery", unique_delivery)
    
    with col2:
        df_filtered['Distance_km'] = df_filtered.apply(calculate_distance, axis=1)
        mean_distance = round(df_filtered['Distance_km'].mean(), 2)
        col2.metric("Average distance", mean_distance)
     
    with col3:
        avg_delivery_time = df_filtered[TIME_COLUMN].mean()
        col3.metric("Avg delivery time", round(avg_delivery_time, 2))
    
    with col4:
        std_delivery_time = df_filtered[TIME_COLUMN].std()
        col4.metric("Std delivery time", round(std_delivery_time, 2))

def display_average_time_by_city(df_filtered):
    """
    Display a bar chart of average delivery time by city, including error bars for standard deviation.
    """
    st.subheader("Average Delivery Time by City")

    df_city_stats = df_filtered.groupby(CITY_COLUMN)[TIME_COLUMN].agg(['mean', 'std']).reset_index()
    df_city_stats.columns = [CITY_COLUMN, 'avg_time', 'std_time']

    fig = go.Figure(go.Bar(
        x=df_city_stats[CITY_COLUMN],
        y=df_city_stats['avg_time'],
        error_y=dict(type='data', array=df_city_stats['std_time'])
    ))

    fig.update_layout(
        xaxis_title="City",
        yaxis_title="Average Delivery Time (min)",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

def display_average_time_by_order_type(df_filtered):
    """
    Display a table of average delivery time by order type for each city.
    """
    st.subheader("Average Time by Order Type")
    
    df_table_stats = df_filtered.groupby([CITY_COLUMN, 'Type_of_order'])[TIME_COLUMN].agg(['mean', 'std']).reset_index()
    df_table_stats.columns = ['City', 'Type_of_order', 'avg_time', 'std_time']
    
    st.dataframe(df_table_stats, height=350)

def display_delivery_time_by_city_traffic(df_filtered):
    """
    Display a box plot of delivery time by city and traffic density.
    """
    st.subheader("Delivery Time by City and Traffic Density")

    fig = px.box(
        df_filtered,
        x=CITY_COLUMN,
        y=TIME_COLUMN,
        color=TRAFFIC_COLUMN,
        labels={TIME_COLUMN: 'Delivery Time (min)', CITY_COLUMN: 'City', TRAFFIC_COLUMN: 'Traffic Density'},
        category_orders={TRAFFIC_COLUMN: ["Low", "Medium", "High", "Jam"]}
    )

    fig.update_layout(
        xaxis_title="City",
        yaxis_title="Delivery Time (min)",
        boxmode='group',
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

# ===========================
# ETL PROCESS
# ===========================

def main():
    st.header('Marketplace - Restaurant View')

    # Configure the sidebar
    date_slider, traffic_options, festival_options = configure_sidebar()

    # Data Extraction
    df = pd.read_csv(FILE_PATH)

    # Data Cleaning and Transformation
    df = clean_data(df)

    # Filter data
    df_filtered = df[(df[ORDER_DATE_COLUMN] <= date_slider) & 
                     (df[TRAFFIC_COLUMN].isin(traffic_options)) & 
                     (df[FESTIVAL_COLUMN].isin(festival_options))]

    # Display the tabs and their content
    tab1, tab2, tab3 = st.tabs(['📊 Management View', '-', '-'])

    with tab1:
        with st.container():
            st.title("Overall Metrics")
            display_overall_metrics(df_filtered)

        with st.container():
            st.markdown("""---""")
            col1, col2 = st.columns([1, 1.5])  # Adjust column proportions

            with col1:
                display_average_time_by_city(df_filtered)

            with col2:
                display_average_time_by_order_type(df_filtered)

        with st.container():
            st.markdown("""---""")
            display_delivery_time_by_city_traffic(df_filtered)

if __name__ == "__main__":
    main()


