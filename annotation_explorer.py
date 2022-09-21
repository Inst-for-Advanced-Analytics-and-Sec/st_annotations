import streamlit as st
import requests
import pandas as pd
import json
from pathlib import Path

# Set tab values for browser
st.set_page_config(
    page_title="Annotation Explorer")

# Define the function to pull annotation data

def get_data():
    init_ann_res = requests.get("http://18.232.136.117:5000/api/noaa/annotations")
    annotations_text = init_ann_res.text
    annotations_json = json.loads(annotations_text)
    annotations_flat = pd.json_normalize(annotations_json['features'], max_level=2)
    annotations_final = annotations_flat
    return annotations_final

# Define function to include markdown file
def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

# Get the data
df = get_data()

# Identify proper dictionaries within the metadata tags column
annotation_data = df[[isinstance(x, dict) for x in df['properties.metadata.tags']]]

# Limit to just jpgs
for_image_tag_counts = annotation_data[annotation_data['properties.metadata.S3Key'].str.contains(".JPG")]

# Push out to columns, sum, and create dataframe
tag_columns = pd.json_normalize(for_image_tag_counts['properties.metadata.tags'])
tag_table = tag_columns.sum(axis=0)
tag_table_2 = pd.DataFrame(tag_table)
tag_table_2.columns = ["Count"]
rounded_tags = tag_table_2.astype(int)

# Plot Markdown & Image
intro_markdown = read_markdown_file("overview.md")
st.markdown(intro_markdown, unsafe_allow_html=True)
st.image("application_diagram.png")

# Plot table of tag counts
st.write("This is the current set of tags along with the number of times they appear in the data.")
st.table(rounded_tags)