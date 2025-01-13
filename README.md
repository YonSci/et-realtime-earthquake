# Ethiopia Real-Time Seismic Activity Monitoring Dashboard <img src="image/et_flag.png" width="50" />


## Introduction

The **Ethiopia Real-Time Seismic Activity Monitoring Dashboard** is an interactive web application designed to monitor and visualize seismic activities across Ethiopia. This user-friendly tool provides real-time data on earthquakes, enabling users to:

- Filter events by time period and magnitude
- View detailed information in tabular format
- Explore earthquake locations on an interactive map

The application retrieves up-to-date earthquake data from the **United States Geological Survey (USGS) Earthquake Catalog API**, a reputable source for global seismic information. It combines real-time data acquisition, robust data processing, and interactive visualization to deliver a comprehensive tool for monitoring earthquakes in Ethiopia. [USGS](https://earthquake.usgs.gov/fdsnws/event/1/quer)

---

## Key Features

- **Time Period Filtering:** Users can select predefined time frames such as the **last 24 hours**, **past 7 days**, or **past 30 days** or **specify custom date ranges** to focus on specific periods of interest.

- **Magnitude Filtering:** Adjustable sliders allow users to set **minimum** and **maximum** **earthquake magnitudes**.

- **Data Presentation:** Filtered earthquake data is displayed in a **clear** and **concise table** format, with options to **download** the dataset for further analysis.

- **Interactive Mapping:** An integrated map visualizes **earthquake epicenters**, with markers that provide detailed information-including **location**, **time**, **magnitude**, and **depth** upon interaction and the map tiles are provided by [OpenStreetMap](https://www.openstreetmap.org/).
---

## Technology Stack

- **Programming Language:** Developed entirely in **Python**, leveraging its extensive ecosystem of data analysis and web development libraries, including `requests`, `pandas`, and `datetime`.

- **Web Framework:** Built using [Streamlit](https://streamlit.io/), an open-source Python framework that enables the rapid development of interactive web applications.

- **Mapping:** Employs [Folium](https://python-visualization.github.io/folium/), a Python library for creating interactive maps, providing users with an intuitive geographical representation of seismic events.
---