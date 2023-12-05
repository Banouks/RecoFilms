import streamlit as st
from st_pages import hide_pages
from PIL import Image

hide_pages("Details")

chemin = './pages'

def image_intro():
    # Affichage de l'image de présentation
    mon_image = Image.open(chemin + '/powerbi.jpeg')
    return mon_image

st.title('Quelques KPI sur PowerBi')
st.write('')

image = image_intro()
st.image(image, width= 800, use_column_width= 'always')

