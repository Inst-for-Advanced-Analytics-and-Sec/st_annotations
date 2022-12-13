import requests
import streamlit as st
from annotation_explorer import get_data
import pandas as pd
import numpy as np
import json
import datetime

# Set page title
st.title('Decision Support Tool')

# Create choice dropdown
expedition_choice = st.sidebar.multiselect("Choose Expeditions", options=["EX1708", "FlowerGardenBanks_YG1901",
                                                   "Bioluminescence", "Cubenet", "select all"])

# select_all_expeditions = st.sidebar.checkbox("select all")

if "select all" in expedition_choice:
    expedition_choice = ["EX1708", "FlowerGardenBanks_YG1901","Bioluminescence", "Cubenet"]

data_type_choice = st.sidebar.multiselect("Which Image Data types", options=["Image", "Video", "Divepath", "select all"])

if "select all" in data_type_choice:
    expedition_choice = ["EX1708", "FlowerGardenBanks_YG1901","Bioluminescence", "Cubenet"]

date = st.sidebar.date_input('Date Range', datetime.date.today())
#st.write(date)

# Get data
df = get_data()

expedtion_list = []

# Limit to proper dictionaries
for i in expedition_choice:
    annotation_data =df[[isinstance(x, dict) and (i in x.keys()) for x in df['properties.metadata.tags']]]
    st.write("*******")
    st.write(annotation_data)
    st.write("*******")
    # Limit to jpegs
    images = annotation_data[annotation_data['properties.metadata.S3Key'].str.contains(".JPG")]

    # Create list of Cloudfront URLs
    for i in images['properties.metadata.S3Key']:
        expedtion_list.append("https://d9we9npuc9dc.cloudfront.net/{}".format(i))

res_expedition = requests.get("http://18.232.136.117:5000/api/noaa/base-expeditions/")
# print(res_expedition)
st.write(res_expedition)
res_text = res_expedition.text
st.write(res_text)
res_json = json.loads(res_text)
st.write(res_json)
res_flat = pd.json_normalize(res_json['features'], max_level=2)
res_final = res_flat
st.write(res_final)
ex_list = res_final['properties.id']
data_list = []

for i in ex_list:
    res_leg = requests.get('http://18.232.136.117:5000/api/noaa/data?expeditionId='+str(i))
    res_leg_text = res_leg.text
    res_leg_json = json.loads(res_leg_text)
    data_list[[i]] = res_leg_json['features']

# m = folium.Map(location=[45.5236, -122.6750])
# folium_static(m)

df = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(df)
# Plot images
#st.image(expedtion_list)