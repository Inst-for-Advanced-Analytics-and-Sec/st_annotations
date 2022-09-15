import streamlit as st
from annotation_explorer import get_data
import pandas as pd

# Set page title
st.title('Image Annotation')

# Create choice dropdown
tag_choice = st.sidebar.multiselect("Tags", options=["Aaptos aaptos", "Corallis polyporum",
                                                   "Hypodytes carinatus", "Lichen ater",
                                                   "Lydia annulipes", "Poritella decidua",
                                                   "Verrucula maritimaria"])

# Get data
df = get_data()

image_list = []

# Limit to proper dictionaries
for i in tag_choice:
    annotation_data =df[[isinstance(x, dict) and (i in x.keys()) for x in df['properties.metadata.tags']]]
    # Limit to jpegs
    images = annotation_data[annotation_data['properties.metadata.S3Key'].str.contains(".JPG")]

    # Create list of Cloudfront URLs
    for i in images['properties.metadata.S3Key']:
        image_list.append("https://d9we9npuc9dc.cloudfront.net/{}".format(i))

# Plot images
st.image(image_list)