import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import branca.colormap as cm
from folium import IFrame, Map, Element
import base64
from pathlib import Path


page_icon = "image/eq1.jpg"


# Set page configuration
st.set_page_config(
    page_title="Ethiopia Earthquake Tracker",
    layout="centered", # Can be "centered" or "wide"
    initial_sidebar_state="expanded",
    page_icon=page_icon
)

st.logo("image/eq1.jpg", size="large")


# Apply custom CSS for styling
st.markdown(
    """
    <style>
    /* Customizing the main title */
    .main-title {
        font-size: 2.5em;
        color: #4CAF50;
        text-align: center;
        font-weight: bold;
    }
    /* Styling the sidebar */
    .sidebar .sidebar-content {
        background-color: #f0f0f5;
    }
    /* Customizing buttons */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 12px;
        font-size: 1em;
        padding: 0.5em 1em;
    }
    /* Customizing expander */
    .st-expander {
        background-color: #e0e0ef;
        border-radius: 10px;
        padding: 1em;
    }
    /* Customizing dataframes */
    .stDataFrame {
        border: 1px solid #ddd;
        border-radius: 10px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state for filters and data if not already present
if 'time_filter' not in st.session_state:
    st.session_state.time_filter = "Last 24 Hours"
if 'min_magnitude' not in st.session_state:
    st.session_state.min_magnitude = 1.0
if 'max_magnitude' not in st.session_state:
    st.session_state.max_magnitude = 8.0
if 'data' not in st.session_state:
    st.session_state.data = None


default_time_filter = "Last 24 Hours"
default_min_magnitude = 1.0
default_max_magnitude = 8.0

# Define a linear colormap for magnitudes
min_magnitude = 1.0
max_magnitude = 7.0
colormap = cm.linear.YlOrRd_09.scale(min_magnitude, max_magnitude)
colormap = colormap.to_step(index=[1, 2, 3, 4, 5, 6])

def convert_to_am_pm(dt):
    return dt.strftime('%Y-%m-%d %I:%M:%S %p')



def fetch_earthquake_data(starttime, endtime, minmagnitude, maxmagnitude):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": starttime,
        "endtime": endtime,
        "minmagnitude": minmagnitude,
        "maxmagnitude": maxmagnitude,
        "minlatitude": 3.4,   # Approximate bounds for Ethiopia
        "maxlatitude": 14.9,
        "minlongitude": 32.9,
        "maxlongitude": 47.9
    }
    response = requests.get(url, params=params)
    data = response.json()
    features = data.get('features', [])
    records = []
    for feature in features:
        properties = feature.get('properties', {})
        geometry = feature.get('geometry', {})
        coordinates = geometry.get('coordinates', [None, None])
        event_time = datetime.utcfromtimestamp(properties.get('time') / 1000.0)
        records.append({
            'time': convert_to_am_pm(event_time),
            'latitude': coordinates[1],
            'longitude': coordinates[0],
            'depth': coordinates[2],
            'magnitude': properties.get('mag'),
            'place': properties.get('place')
        })
    df = pd.DataFrame(records)
    # rename columns
    df.rename(columns={'time': 'Time', 'latitude': 'Latitude', 'longitude': 'Longitude', 'depth': 'Depth', 'magnitude': 'Magnitude', 'place': 'Location'}, inplace=True)
    return df

# Function to fetch data based on current filters
def fetch_and_store_data(start_date, end_date, min_magnitude, max_magnitude):
    data = fetch_earthquake_data(
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
        min_magnitude,
        max_magnitude
    )
    st.session_state.data = data

# Determine default date range for "Last 24 Hours"
end_date_default = datetime.now()
start_date_default = end_date_default - timedelta(days=1)

# Fetch data on initial load if not already fetched
if st.session_state.data is None:
    fetch_and_store_data(start_date_default, end_date_default, st.session_state.min_magnitude, st.session_state.max_magnitude)


# Initialize session state for data if not already present
if 'data' not in st.session_state:
    st.session_state.data = None

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


def img_to_html(img_path):
    img_html = "<img src='data:image/png;base64,{}' style='width:80px;' class='img-fluid'>".format(
      img_to_bytes(img_path)
    )
    return img_html    

# Main title

st.markdown(f"<h1 class='main-title'>Ethiopian Real-Time Seismic Activity Monitoring Dashboard {img_to_html('./image/et_flag.png')} </h1>", unsafe_allow_html=True)


# Sidebar for filters
with st.sidebar:
    st.header("Filter Options")

    # Time Period Filter
    time_filter = st.selectbox(
        "Select Time Period",
        ["Last 24 Hours", "Past 7 Days", "Past 30 Days", "Custom Date Range"],
        index=["Last 24 Hours", "Past 7 Days", "Past 30 Days", "Custom Date Range"].index(st.session_state.time_filter)
    )

    if time_filter == "Custom Date Range":
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
        end_date = st.date_input("End Date", value=datetime.now())
    else:
        end_date = datetime.now()
        if time_filter == "Last 24 Hours":
            start_date = end_date - timedelta(days=1)
        elif time_filter == "Past 7 Days":
            start_date = end_date - timedelta(days=7)
        elif time_filter == "Past 30 Days":
            start_date = end_date - timedelta(days=30)

    # Magnitude Filter
    min_magnitude = st.slider("Minimum Magnitude", 0.0, 10.0, st.session_state.min_magnitude)
    max_magnitude = st.slider("Maximum Magnitude", 0.0, 10.0, st.session_state.max_magnitude)


    # Fetch Data Button
    if st.button("Fetch Data"):
        fetch_and_store_data(start_date, end_date, min_magnitude, max_magnitude)
        st.session_state.time_filter = time_filter
        st.session_state.min_magnitude = min_magnitude
        st.session_state.max_magnitude = max_magnitude


   # subtitle
st.markdown('<h2 class="main-subtitle">Data Tabel</h2>', unsafe_allow_html=True)

# Main content area
# Check if data is available
if st.session_state.data is not None and not st.session_state.data.empty:
    data = st.session_state.data

    # Display data in an expander
    with st.expander("View Data Table", expanded=True):
        st.dataframe(data)

        # Download data as CSV
        csv = data.to_csv(index=False)
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name='earthquake_data.csv',
            mime='text/csv',
        )


    # Plotting the bar chart



# Map Visualization

    def create_popup_html(place, time, magnitude, depth):
        html = f"""
        <div style="font-family: Arial; font-size: 11px; padding: 10px;">
            <p style="margin: 0;"><strong>Place:</strong> {place} km</p>
            <p style="margin: 0;"><strong>Time:</strong> {time}</p>
            <p style="margin: 0;"><strong>Magnitude:</strong> {magnitude}</p>
            <p style="margin: 0;"><strong>Depth:</strong> {depth} km</p>
        </div>
        """
        return html

    # subtitle
    st.markdown('<h2 class="main-subtitle"> Interactive Map </h2>', unsafe_allow_html=True)


    m = folium.Map(location=[9.145, 40.489673], zoom_start=7)


    # Add base layers
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)

    folium.TileLayer('CartoDB Positron',
                     name='CartoDB Positron',
                     attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.').add_to(m)
    
  

    earthquake_layer = folium.FeatureGroup(name='Earthquake Markers')


    # Add circle markers to the map
    for _, row in data.iterrows():
        popup_html = create_popup_html(
            place=row['Location'],
            time=row['Time'],
            magnitude=row['Magnitude'],
            depth=row['Depth']
        )
        iframe = IFrame(popup_html, width=250, height=100)
        popup = folium.Popup(iframe, max_width=250)
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=row['Magnitude'] * 1,
            popup=popup,
            color=colormap(row['Magnitude']),
            fill=True,
            fill_color=colormap(row['Magnitude']),
            fill_opacity=0.8
            ).add_to(earthquake_layer)
        earthquake_layer.add_to(m)


    folium.LayerControl(position='topleft').add_to(m)



    # Add colormap legend to the map
    colormap.caption = 'Earthquake Magnitude'
    # colormap.position = 'bottomright'
    colormap.add_to(m)


    # Display the map in the Streamlit app
    st_folium(m, width=700, height=450)
else:
    st.warning("No data available. Please adjust the filters and fetch data.")

# Earthquake Occurrences
st.markdown('<h2 class="main-subtitle">Daily Earthquake Occurrences </h2>', unsafe_allow_html=True)

# Check if 'data' exists in session state and is valid
if 'data' in st.session_state and st.session_state.data is not None and not st.session_state.data.empty:
    data = st.session_state.data  # Retrieve data from session state
    
    # Ensure the 'Time' column exists
    if 'Time' in data.columns:
        # Convert 'Time' to datetime
        data['Time'] = pd.to_datetime(data['Time'])
        
        # Extract the date part
        data['Date'] = data['Time'].dt.date
        
        # Count occurrences by date
        daily_counts = data['Date'].value_counts().sort_index()

        # Handle cases where there is only one data point
        if len(daily_counts) == 1:
            single_date = daily_counts.index[0]
            next_day = pd.Series([0], index=[single_date + timedelta(days=1)])
            daily_counts = pd.concat([daily_counts, next_day])

        # Convert to DataFrame for visualization
        daily_counts_df = daily_counts.reset_index()
        daily_counts_df.columns = ['Date', 'Number of Earthquakes']

        # Display data in an expander
        with st.expander("View Data Table", expanded=True):
            st.dataframe(daily_counts_df)

            # Download data as CSV
            csv = daily_counts_df.to_csv(index=False)
            st.download_button(
                label="Download Data as CSV",
                data=csv,
                file_name='earthquake_data_count.csv',
                mime='text/csv',
            )

        # Bar chart visualization
        st.markdown('<h3 class="main-subtitle">Bar Chart for Daily Earthquake Occurrences</h3>', unsafe_allow_html=True)
        
        fig = px.bar(
            daily_counts_df,
            x='Date',
            y='Number of Earthquakes',
            labels={'Date': 'Date', 'Number of Earthquakes': 'Number of Earthquakes'},
            title='Earthquake Occurrences',
            template='plotly_white'
        )

        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Number of Earthquakes',
            xaxis=dict(tickformat='%Y-%m-%d'),
            bargap=0.2
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("The 'Time' column is missing in the fetched data.")
else:
    st.warning("No earthquake data is available. Please adjust the filters and fetch data.")





















# # Convert 'Time' to datetime
# data['Time'] = pd.to_datetime(data['Time'])
# #data['Time'] = pd.to_datetime(data['Time'], format='%Y-%m-%d %H:%M:%S')
# # Extract date part
# data['Date'] = data['Time'].dt.date
# # Count occurrences
# daily_counts = data['Date'].value_counts().sort_index()
# # Handle single data point
# if len(daily_counts) == 1:
#     single_date = daily_counts.index[0]
#     # Create a new Series with the next day's date and a count of 0
#     next_day = pd.Series([0], index=[single_date + timedelta(days=1)])
#     # Concatenate the original Series with the new Series
#     daily_counts = pd.concat([daily_counts, next_day])

# # Convert to DataFrame for Plotly
# daily_counts_df = daily_counts.reset_index()
# daily_counts_df.columns = ['Date', 'Number of Earthquakes']

# # Display data in an expander
# with st.expander("View Data Table", expanded=True):
#     st.dataframe(daily_counts_df)

#     # Download data as CSV
#     csv = daily_counts_df.to_csv(index=False)
#     st.download_button(
#         label="Download Data as CSV",
#         data=csv,
#         file_name='earthquake_data_count.csv',
#         mime='text/csv',
#     )

# st.markdown('<h3 class="main-subtitle">Bar chart for daily earthquake occurrences</h3>', unsafe_allow_html=True)

# fig = px.bar(
#     daily_counts_df,
#     x='Date',
#     y='Number of Earthquakes',
#     labels={'Date': 'Date', 'Number of Earthquakes': 'Number of Earthquakes'},
#     title='Earthquake Occurrences',
#     template='plotly_white'
# )

# fig.update_layout(
#     xaxis_title='Date',
#     yaxis_title='Number of Earthquakes',
#     xaxis=dict(tickformat='%Y-%m-%d'),
#     bargap=0.2
# )

# st.plotly_chart(fig, use_container_width=True)
