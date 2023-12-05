import streamlit as st
from st_pages import hide_pages
from PIL import Image

hide_pages("Details")

chemin = './pages'

def image_intro():
    # Affichage de l'image de présentation
    mon_image = Image.open(chemin + '/question-mark.png')
    return mon_image

st.title('Vous avez des questions ?')
st.write('')

image = image_intro()
st.image(image, width= 600)