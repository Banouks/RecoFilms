import streamlit as st
from st_pages import hide_pages
from PIL import Image

hide_pages("Details")

st.title('Quelques chiffres clés sur les données')

chemin = './pages'

@st.cache_data(ttl=24*60*60)
def image_intro():
    # Affichage de l'image de présentation
    mon_image = Image.open(chemin + '/data.png')
    return mon_image

image = image_intro()
st.image(image, width= 800, use_column_width= 'always')
