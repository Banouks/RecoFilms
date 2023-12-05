

import streamlit as st
from st_pages import Page, show_pages, Section, hide_pages
from PIL import Image

hide_pages("Details")

chemin = './pages'

def image_intro():
    # Affichage de l'image de présentation
    mon_image = Image.open(chemin + '/superhero2.jpg')
    return mon_image

st.title('Welcome to :')
st.header('Projet 2 "Recommandation de films"')

image = image_intro()
st.image(image, width= 800, use_column_width= 'always')

st.subheader("Staring : Audrey, Aimé, and Florent !")
show_pages(
    [
        Page("./Main.py", "Introduction", "🏠"),
        Page(chemin + "/KPImacro.py", "KPI macro", ":bar_chart:"),
        Page(chemin + "/Application.py", "Application", ":tv:"),
        Page(chemin + "/Details.py", "Details", ":books:"),
    ]
)
