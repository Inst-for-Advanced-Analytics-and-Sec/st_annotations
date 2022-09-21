import streamlit as st
from annotation_explorer import get_data
import pymongo as pm
import bson, requests, os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import json
import pandas as pd

user = 'bausdenmoore'
password = 'KBfV0wXEgDYXEnNh'

clientString = ['mongodb+srv://' + user + ':' + password + '@clustersaptest.i1ivo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority']
client = pm.MongoClient(clientString, ssl=True, ssl_cert_reqs='CERT_NONE')
mydb = client["AquaView"]
AnnotationCol = mydb["Annotations"]

# Set page title
st.title('Image w/ Annotation Display')

# Create choice dropdown
tag_choice = st.sidebar.multiselect("Tags", options=["Aaptos aaptos", "Corallis polyporum",
                                                   "Hypodytes carinatus", "Lichen ater",
                                                   "Lydia annulipes", "Poritella decidua",
                                                   "Verrucula maritimaria", "Blastomussa omanensis"])
image_list = []
image_id = []
annotation_list = []

# init_ann_res = requests.get("http://18.232.136.117:5000/api/noaa/annotations")
# annotations_text = init_ann_res.text
# annotations_json = json.loads(annotations_text)
# annotations_flat = pd.json_normalize(annotations_json['features'], max_level=2)
# annotations_final = annotations_flat
# df = annotations_final

df_2 = get_data()

# Limit to proper dictionaries
for i in tag_choice:
    annotation_data =df_2[[isinstance(x, dict) and (i in x.keys()) for x in df_2['properties.metadata.tags']]]
    # Limit to jpegs
    images = annotation_data[annotation_data['properties.metadata.S3Key'].str.contains(".JPG")]

    # Create list of Cloudfront URLs
    for idx, img in images.iterrows():
        image_id.append({img['properties.id']})
        image_list.append("https://d9we9npuc9dc.cloudfront.net/{}".format(img['properties.metadata.S3Key']))
        queryString = {
            '_id': bson.ObjectId(img['properties.id'])
            }
        annotation_list.append([AnnotationCol.find_one(queryString)])

st.sidebar.text(f'Total Images: {len(image_list)}')
image_choice = st.sidebar.number_input("Which Image?", min_value=0, max_value=len(image_list))

# Plot images
TINT_COLOR = (0, 255, 0)  # Green
TRANSPARENCY = .25  # Degree of transparency, 0-100%
OPACITY = int(255 * TRANSPARENCY)

try:
    response = requests.get(image_list[image_choice])
    image = Image.open(BytesIO(response.content))

    overlay = Image.new('RGBA', image.size, TINT_COLOR+(0,))
    draw = ImageDraw.Draw(overlay)  # Create a context for drawing things on it.

    for anno in annotation_list[image_choice]:
        for obj in anno['objects']:
            genus = anno['objects'][obj]['label']['genus']
            species = anno['objects'][obj]['label']['species']
            instanceId = anno['objects'][obj]['label']['instance_id']
            label = f'{genus} {species} ({instanceId})'
            bbox = [anno['objects'][obj]['bbox']['x'],
                    anno['objects'][obj]['bbox']['y'],
                    anno['objects'][obj]['bbox']['width'],
                    anno['objects'][obj]['bbox']['height']]
            draw.rectangle(((bbox[0]-bbox[2]/2, bbox[1]-bbox[3]/2), (bbox[0]+bbox[2]/2, bbox[1]+bbox[3]/2)), fill=TINT_COLOR+(OPACITY,))
            draw.text((bbox[0]-bbox[2]/2, bbox[1]-bbox[3]/2-50), label,
                      font = ImageFont.truetype(os.path.join(os.getcwd(), 'font', 'arial.ttf'), 50))
    st.image(Image.alpha_composite(image.convert('RGBA'), overlay))
except:
    st.text("Try Another Image")