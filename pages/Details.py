import streamlit as st
import pandas as pd
import numpy as np
from streamlit_extras.switch_page_button import switch_page
from PIL import Image
import urllib.request
from st_pages import hide_pages
import json
import requests

hide_pages("Details")

st.title('Et pourquoi pas ce film ? ')
st.write('')

df_tmdb = st.session_state.df_tmdb
df_films = st.session_state.df_films
mon_tconst = st.session_state.mon_tconst
df_tmdb = df_tmdb[df_tmdb['tconst'] == mon_tconst]
df_films = df_films[df_films['tconst'] == mon_tconst]

chemin = st.session_state.chemin
path_image = st.session_state.path_image

def recherche_casting(un_id, un_df):
    # Récupération du casting dans une liste en spératant les personnes
    récuperation = un_df[un_df['tconst'] == un_id]['primaryName']\
        .apply(lambda x : x.split(sep=','))
    # Transformation en liste
    liste = récuperation.iloc[0]
    # Limitation aux 3 1eere personnes
    if len(liste) > 6 :
        liste = liste[:6]
    return liste

def load_image_from_github(url):
  with urllib.request.urlopen(url) as response:
    image = Image.open(response)
  return image

col1, col2, col3 = st.columns([3, 2, 3])
with col1 :
            # Affichage du film sélectionné
            if df_films[df_films['tconst'] == mon_tconst]['poster_path'].item() != 'None' : 
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == mon_tconst]['poster_path'].item())
            else : 
                image_film = Image.open(chemin + '/image-non-disponible.png')
            st.image(image_film, width= 200)
            st.write(df_films[df_films['tconst'] == mon_tconst]['originalTitle'].item())
with col2 :
            st.subheader("Note : " + str(df_films[df_films['tconst'] == mon_tconst]['averageRating'].item()))
            st.subheader('Casting :')
            max_cast = 0
            for cast in recherche_casting(mon_tconst, df_films) :
                st.write(cast)
with col3 :
            st.subheader('Synopsis :')
            st.write(str(df_tmdb[df_tmdb['tconst'] == mon_tconst]['overview'].item()))

id_tmdb = df_films[df_films['tconst'] == mon_tconst]['id'].item()

test = requests.get('https://api.themoviedb.org/3/movie/' + str(id_tmdb) + '/videos?api_key=75be780e29e5de2e576bc41b8259541e')

if test.status_code == 200 :
    
    test = test.json()
    code_youtube = test['results'][0]['key']
    st.video('https://youtu.be/' + code_youtube)

back = st.button('Back to list')
if back :
    switch_page("application")