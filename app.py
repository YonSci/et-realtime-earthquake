import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="Ethiopia Earthquake Tracker",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

# Function to fetch earthquake data from USGS API
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
        records.append({
            'time': datetime.utcfromtimestamp(properties.get('time') / 1000.0),
            'latitude': coordinates[1],
            'longitude': coordinates[0],
            'depth': coordinates[2],
            'magnitude': properties.get('mag'),
            'place': properties.get('place')
        })
    df = pd.DataFrame(records)
    return df

# Initialize session state for data if not already present
if 'data' not in st.session_state:
    st.session_state.data = None

# Main title
st.markdown('<h1 class="main-title">Ethiopia Earthquake Tracker 🌍</h1>', unsafe_allow_html=True)

# Sidebar for filters
with st.sidebar:
    st.header("Filter Options")

    # Time Period Filter
    time_filter = st.selectbox("Select Time Period", ["Last 24 Hours", "Past 7 Days", "Past 30 Days", "Custom Date Range"])

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
    min_magnitude = st.slider("Minimum Magnitude", 0.0, 10.0, 2.5)
    max_magnitude = st.slider("Maximum Magnitude", 0.0, 10.0, 8.0, 8.0)

    # Fetch Data Button
    if st.button("Fetch Data"):
        st.session_state.data = fetch_earthquake_data(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            min_magnitude,
            max_magnitude
        )

# Main content area
if st.session_state.data is not None:
    if not st.session_state.data.empty:
        # Displaying data in an expander
        with st.expander("View Data Table", expanded=True):
            st.dataframe(st.session_state.data)

            # Download data as CSV
            csv = st.session_state.data.to_csv(index=False)
            st.download_button(
                label="Download Data as CSV",
                data=csv,
                file_name='earthquake_data.csv',
                mime='text/csv',
            )

        # Map Visualization
        st.subheader("Map Visualization")
        m = folium.Map(location=[9.145, 40.489673], zoom_start=5)
        for _, row in st.session_state.data.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=row['magnitude'] * 2,
                popup=(
                    f"Location: {row['place']}<br>"
                    f"Time: {row['time']}<br>"
                    f"Magnitude: {row['magnitude']}<br>"
                    f"Depth: {row['depth']} km"
                ),
                color='crimson',
                fill=True,
                fill_color='crimson'
            ).add_to(m)
        st_folium(m, width=700, height=450)
    else:
        st.write("No earthquake data found for the selected criteria.")
else:
    st.write("Use the filters in the sidebar to fetch earthquake data.")
