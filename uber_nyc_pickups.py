import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import time

st.title('Uber pickups in NYC')


DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')


def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data


# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')

# Load 10,000 rows of data into the dataframe.
data = load_data(10000)

# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

if st.checkbox('Show bar chart'):
    st.subheader('Number of pickups by hour')

    hist_values = np.histogram(
        data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]

    st.bar_chart(hist_values)


hour_to_filter = st.slider('Hour to filter', min_value=0, max_value=23, value=17)
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]


st.subheader(f'Map of all pickups at {hour_to_filter}:00')

st.map(filtered_data)


st.subheader(f"3D Map of all pickups at {hour_to_filter}:00")

# Render 3D Hexagon/Column map
st.pydeck_chart(
    pdk.Deck(
        map_style="light",
        initial_view_state=pdk.ViewState(
            latitude=filtered_data["lat"].mean(),
            longitude=filtered_data["lon"].mean(),
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=filtered_data,
                get_position="[lon, lat]",
                radius=200,  # Size of hexagons in meters
                elevation_scale=50,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ],
    )
)

st.subheader(f"2D Heat Map of all pickups at {hour_to_filter}:00")

st.pydeck_chart(
    pdk.Deck(
        map_style="light",
        initial_view_state=pdk.ViewState(
            latitude=filtered_data["lat"].mean(),
            longitude=filtered_data["lon"].mean(),
            zoom=11,
            pitch=50,
        ),
        layers = [
    pdk.Layer(
        "HeatmapLayer",
        data=filtered_data,
        get_position="[lon, lat]",
        aggregation=pdk.types.String("SUM"),
        get_weight="1",  # Gives every pickup equal weight
        radius_pixels=60,  # Glow radius of hotspots
    )
],
    )
)



if st.button("▶️ Play 24-Hour Time-Lapse"):
    # Create an empty placeholder container to dynamically swap maps
    map_placeholder = st.empty()
    
    # 1. Start at hour 0
    hour = 0
    
    # 2. Loop indefinitely
    while True:
        # Update dataset filter iteratively
        hourly_data = data[data[DATE_COLUMN].dt.hour == hour]
        
        # Render map directly into the placeholder
        with map_placeholder.container():
            st.markdown(f"### Current Hour: {hour:02d}:00")
            st.pydeck_chart(pdk.Deck(
                map_style="dark",
                initial_view_state=pdk.ViewState(latitude=40.75, longitude=-73.98, zoom=11, pitch=40),
                layers=[pdk.Layer("HeatmapLayer", data=hourly_data, get_position="[lon, lat]", radius_pixels=40)]
            ))
        
        time.sleep(0.7)  # Controls animation speed
        
        # 3. Advance to the next hour, resetting to 0 when it hits 24
        hour = (hour + 1) % 24
