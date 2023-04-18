import streamlit as st
from datetime import datetime
import requests
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap

@st.cache
def get_data():
    init_ann_res = requests.get("http://34.227.61.39:5000/api/noaa/base-expeditions/")
    annotations_text = init_ann_res.text
    annotations_json = json.loads(annotations_text)
    annotations_flat = pd.json_normalize(annotations_json['features'], max_level=2)
    annotations_final = annotations_flat
    return annotations_final


base_expeditions = get_data()

expedition_list = [x for x in
                   base_expeditions["properties.id"]]  # expedition ID to make expedition specific data request.
expeditions = [x for x in base_expeditions["properties.cruiseIdentifier"]]  # to display expedition names on screen.

data_list = []
for i in expedition_list:
    res_leg = requests.get("http://34.227.61.39:5000/api/noaa/data?expeditionId=" + i)
    res_data = res_leg.text
    res_json = json.loads(res_data)
    dd = pd.json_normalize(res_json['features'], max_level=2)
    data_list.append(pd.json_normalize(res_json['features'], max_level=2))

df = pd.concat(data_list)
df = df.drop(df[df['properties.expeditionName'] == "CubeNet"].index)
df[["lon", "lat"]] = pd.DataFrame(df["geometry.coordinates"].tolist(), index=df.index)

final_data = pd.merge(df, base_expeditions[
    ["properties.id", "properties.cruiseStartDate", "properties.cruiseEndDate", "properties.cruiseAbstract"]],
                      left_on="properties.expeditionId", right_on="properties.id", how='left')

final_data['properties.cruiseStartDate'] = pd.to_datetime(final_data['properties.cruiseStartDate'])
final_data['properties.cruiseEndDate'] = pd.to_datetime(final_data['properties.cruiseEndDate'])

# -------------------On Screen-------------------------

# Set page title
st.title('Decision Support Tool')

# Create choice dropdown
date_range = st.sidebar.slider("Date_Range", min_value=datetime(2015, 1, 14), max_value=datetime(2019, 9, 1),
                               value=[datetime(2015, 1, 14), datetime(2019, 9, 1)], label_visibility="visible")

Choose_Expeditions = st.sidebar.multiselect("Choose_Expeditions", default=expeditions, options=expeditions)
type = ["Image", "Video", "DivePath"]

data_type = st.sidebar.multiselect("Which Data Types", default=type, options=type)

data_data = final_data.loc[(final_data['properties.cruiseStartDate'] >= date_range[0]) & (
        final_data['properties.cruiseEndDate'] <= date_range[1]) & (
                               final_data['properties.expeditionName'].isin(Choose_Expeditions)) & (
                               final_data['properties.dataType'].isin(data_type)) & (final_data['lat'] > 0)]

st.map(data_data)

# #code for heatMap
# data_data['lat'] = data_data['lat'].astype(float)
# data_data['lon'] = data_data['lon'].astype(float)
#
#
# # Creating folium Map
# my_map = folium.Map(location=[28.077606, -92.005118], zoom_start=3, min_zoom=3)
#
# # creating heat map
# heat_data = [[row['lat'], row['lon']] for index, row in data_data.iterrows()]
# HeatMap(heat_data).add_to(my_map)

# # Displaying map
# st_data = st_folium(my_map, width=5000)
