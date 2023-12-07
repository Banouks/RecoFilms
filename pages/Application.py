#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from PIL import Image
import urllib.request
from st_clickable_images import clickable_images
from streamlit_extras.switch_page_button import switch_page
from st_pages import hide_pages
import zipfile


hide_pages("Details")

recherche = ''
touslesfilms = []
multiple_films = []
path_image = 'https://image.tmdb.org/t/p/w500'
chemin = './pages'

st.session_state.chemin = chemin
st.session_state.path_image = path_image

# Importation des dataframes
@st.cache_resource
def readcsv():
    zf1 = zipfile.ZipFile(chemin + '/df_films.csv.zip') 
    zf2 = zipfile.ZipFile(chemin + '/df_tmdb.csv.zip') 
    df1 = pd.read_csv(zf1.open('df_films.csv'), sep = ',')
    df2 = pd.read_csv(zf2.open('df_tmdb.csv'), sep = ',')
    df1 = df1.sort_values(by= 'popularity', ascending= False)
    # Je remplit les valeurs null
    df1.fillna('None', inplace= True)
    df2.fillna('None', inplace= True)
    return df1, df2

if 'df_films' not in st.session_state :
    df_films, df_tmdb = readcsv()
    st.session_state.df_films = df_films
    st.session_state.df_tmdb = df_tmdb

df_films = st.session_state.df_films
df_tmdb = st.session_state.df_tmdb 

# je fais la liste des films du df_films pour la placer dans la liste déroulante
@st.cache_resource
def liste_films(un_df) :
    liste = []
    liste = un_df['originalTitle_Year'].to_list()
    st.session_state.liste_films = liste

# je récupère le tconst du film à partir du titre du film qui sera sélectionné dans la liste déroulante
def recherche_tconst_film(titre_film) :
    st.session_state.titre_film = titre_film
    choix = df_films[df_films['originalTitle_Year'] == titre_film]['tconst'].values
    return choix

# Fonction qui permettra de récupérer automatiquement les paramètres pour le ML
def parametre_film(un_index, un_df):
        
        #Je récupère les paramètres du film correspondant au tconst récupéré dans la fonction recherche_film
        parametreFilm = un_df[un_df['tconst'] == un_index[0]]\
                        [['original_language', 'startYear2', 'firstGenre', 'secondGenre', \
                         'averageRating2', 'numVotes2', 'popularity2']]

        return parametreFilm

# Recherche du casting correspondant à un film en fonction du tcont du film / renvoi la liste du casting
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

# Recherche des films avec une liste de personnes, recherche par index de la liste, renvoi une liste de tconst
def rech_film_par_cast(une_liste, un_index, un_df) :
    un_df = un_df.loc[un_df['primaryName'].str.contains(une_liste[un_index])]
    un_df = un_df.sort_values(by= 'popularity', ascending= False)['tconst'].head(6)
    films = un_df.to_list()
    return films

# Récupère une image à partir d'une URL
def load_image_from_github(url):
  with urllib.request.urlopen(url) as response:
    image = Image.open(response)
  return image

@st.cache_resource
def mlKNN():
    # On va récupérer les plus proches voisins du film recherché
    X = df_films[['original_language', 'startYear2', 'firstGenre', 'secondGenre', \
            'averageRating2', 'numVotes2', 'popularity2']]

    # Apprentissage sur x voisins
    entrainement = NearestNeighbors(n_neighbors= 13).fit(X)
    return entrainement

def affiche_image(une_liste, un_index):
    
    if df_films[df_films['tconst'] == une_liste[un_index]]['poster_path'].item() != 'None' :
        image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == une_liste[un_index]]['poster_path'].item())
    else :
        image_film = Image.open(chemin + '/image-non-disponible.png')
    st.image(image_film, width= 200, use_column_width= 'always')
    st.write(df_films[df_films['tconst'] == une_liste[un_index]]['originalTitle'].item())

# affiche tous les films recommandés
def affiche_film_film(une_liste, un_index):

    if df_films[df_films['tconst'] == une_liste[un_index]]['poster_path'].item() == 'None' :
        clicked = clickable_images(['https://www.ville.magog.qc.ca/bibliotheque/wp-content/uploads/2015/09/image-non-disponible.png'],
                        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
                        img_style={"margin": "0px", "height": "160px"},
                        key = une_liste[un_index] + 'film')  
        st.markdown(click_image(une_liste[un_index]) if clicked > -1 else '')
    else :
        clicked = clickable_images([path_image + df_films[df_films['tconst'] == une_liste[un_index]]['poster_path'].item()],
                        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
                        img_style={"margin": "0px", "height": "160px"},
                        key = une_liste[un_index] + 'film')      
        st.markdown(click_image(une_liste[un_index]) if clicked > -1 else '') 
    st.write(df_films[df_films['tconst'] == une_liste[un_index]]['originalTitle'].item())
    #st.markdown(click_image(une_liste[un_index]) if clicked > -1 else '')

def affiche_film_casting(une_liste, un_index, casting):

    if df_films[df_films['tconst'] == une_liste[un_index]]['poster_path'].item() == 'None' :
        clicked = clickable_images(['https://www.ville.magog.qc.ca/bibliotheque/wp-content/uploads/2015/09/image-non-disponible.png'],
                        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
                        img_style={"margin": "0px", "height": "160px"},
                        key = une_liste[un_index]+ casting)  
        st.markdown(click_image(une_liste[un_index]) if clicked > -1 else '')
    else :
        clicked = clickable_images([path_image + df_films[df_films['tconst'] == une_liste[un_index]]['poster_path'].item()],
                        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
                        img_style={"margin": "0px", "height": "160px"},
                        key = une_liste[un_index]+ casting)      
        st.markdown(click_image(une_liste[un_index]) if clicked > -1 else '') 
    st.write(df_films[df_films['tconst'] == une_liste[un_index]]['originalTitle'].item())

#action lors du clic sur une image pour accèder à au détail du film
def click_image(un_tconst):
    st.session_state.mon_tconst = un_tconst
    switch_page("Details")

# action lors du clic sur la liste déroulante et donc choix d'un titre de film
def submit_select():
    st.session_state.titre_film = st.session_state.select
    st.session_state.index_film = df_films[df_films['originalTitle_Year'] == st.session_state.titre_film].index.values

filmKNN = mlKNN()

@st.cache_data(ttl=60*10)
def image_intro():
    # Affichage de l'image de présentation
    mon_image = Image.open(chemin + '/Chanmel 2.jpg')
    return mon_image

image = image_intro()
st.image(image, width= 800, use_column_width= 'always')

st.write('Welcome back to your Chanmel account you tv shows addict')

#if 'liste_films' not in st.session_state :
#     liste_films(df_films)

# Accrémentation de la selectbox avec les films trouvé    
if 'titre_film' not in st.session_state :
    titre_film = st.selectbox('Sélectionnez un film dans la liste :', df_films['originalTitle_Year'], index= None,  key= 'select', \
                                on_change= submit_select)
    #st.session_state.titre_film = titre_film
    
    st.session_state.titre_film + '  1'
else : 
    
    st.session_state.titre_film + '  2'
    st.session_state.index_film
    index = st.session_state.index_film
    index
    df_films['originalTitle_Year'][index]
    titre_film = st.session_state.titre_film
    st.selectbox('Sélectionnez un film dans la liste :', df_films['originalTitle_Year'], index= int(st.session_state.index_film), \
                               key= 'select', on_change= submit_select)
    titre_film = st.session_state.titre_film                         
    titre_film + '     4'
    #st.session_state.titre_film = titre_film        
    st.session_state.titre_film + '  3'                   
#else :
#    titre_film = st.session_state.titre_film
#    titre_film = st.selectbox('Sélectionnez un film dans la liste :', liste_films(df_films), index= titre_film, \
#                                           key= 'select', on_change= submit_select)
 
    if titre_film :
        st.divider()

        tconst_film = recherche_tconst_film(titre_film)
        st.session_state.tconst_film = tconst_film
        #st.session_state.tconst_film = recherche_tconst_film(titre_film)
        #st.session_state.tconst_film
        #tconst_film
        # Je fais ma recherche de voisin et j'affiche les résultats (retourne les index)
        ideeFilm = filmKNN.kneighbors(parametre_film(st.session_state.tconst_film, df_films))
        #ideeFilm
        # Récupération des tconst vaec les index des films
        montconst = []
        for item in ideeFilm[1][0][:] :
            montconst.append(df_films.iloc[item]['tconst'])
        
        liste_casting = recherche_casting(montconst[0], df_films)

        col1, col2, col3 = st.columns([3, 2, 3])
        with col1 :
                # Affichage du film sélectionné
                st.subheader('Film sélectionné :')
                if df_films[df_films['tconst'] == montconst[0]]['poster_path'].item() != 'None' : 
                    image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == montconst[0]]['poster_path'].item())
                else : 
                    image_film = Image.open(chemin + '/image-non-disponible.png')
                st.image(image_film, width= 200)
                st.write(df_films[df_films['tconst'] == montconst[0]]['originalTitle'].item())
        with col2 :
                st.subheader("Note : " + str(df_films[df_films['tconst'] == montconst[0]]['averageRating'].item()))
                st.subheader('Casting :')
                max_cast = 0
                for cast in liste_casting :
                    st.write(cast)
        with col3 :
                st.subheader('Synopsis :')
                st.write(str(df_tmdb[df_tmdb['tconst'] == montconst[0]]['overview'].item()))

        st.divider()
    
            # Je crée des colonnes pour afficher les images des films voisins
        st.header('Voici nos recommandations')

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1 :
                affiche_film_film(montconst, 1)
        with col2 :
                affiche_film_film(montconst, 2)
        with col3 :
                affiche_film_film(montconst, 3)
        with col4 :
                affiche_film_film(montconst, 4)
        with col5 :
                affiche_film_film(montconst, 5)
        with col6 :
                affiche_film_film(montconst, 6)

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1 :
                affiche_film_film(montconst, 7)
        with col2 :
                affiche_film_film(montconst, 8)
        with col3 :
                affiche_film_film(montconst, 9)
        with col4 :
                affiche_film_film(montconst, 10)
        with col5 :
                affiche_film_film(montconst, 11)
        with col6 :
                affiche_film_film(montconst, 12)
        
        st.divider()

        liste_film_par_casting = []
        liste_film_par_casting = rech_film_par_cast(liste_casting, 1, df_films)

        st.header('Films avec ' + liste_casting[1])
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1 :
                if len(liste_film_par_casting) > 0 :
                    affiche_film_casting(liste_film_par_casting, 0, liste_casting[0])
                    if len(liste_film_par_casting) > 1 :
                        with col2 :
                            affiche_film_casting(liste_film_par_casting, 1, liste_casting[0])
                            if len(liste_film_par_casting) > 2 :
                                with col3 :
                                    affiche_film_casting(liste_film_par_casting, 2, liste_casting[0])
                                    if len(liste_film_par_casting) > 3 :
                                        with col4 :
                                            affiche_film_casting(liste_film_par_casting, 3, liste_casting[0])
                                            if len(liste_film_par_casting) > 4 :
                                                with col5 :
                                                    affiche_film_casting(liste_film_par_casting, 4, liste_casting[0])
                                                    if len(liste_film_par_casting) > 5 :
                                                        with col6 :
                                                            affiche_film_casting(liste_film_par_casting, 5, liste_casting[0])

        st.divider()

        liste_film_par_casting = []
        liste_film_par_casting = rech_film_par_cast(liste_casting, 2, df_films)

        st.header('Films avec ' + liste_casting[2])
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1 :
                if len(liste_film_par_casting) > 0 :
                    affiche_film_casting(liste_film_par_casting, 0, liste_casting[1])
                    if len(liste_film_par_casting) > 1 :
                        with col2 :
                            affiche_film_casting(liste_film_par_casting, 1, liste_casting[1])
                            if len(liste_film_par_casting) > 2 :
                                with col3 :
                                    affiche_film_casting(liste_film_par_casting, 2, liste_casting[1])
                                    if len(liste_film_par_casting) > 3 :
                                        with col4 :
                                            affiche_film_casting(liste_film_par_casting, 3, liste_casting[1])
                                            if len(liste_film_par_casting) > 4 :
                                                with col5 :
                                                    affiche_film_casting(liste_film_par_casting, 4, liste_casting[1])
                                                    if len(liste_film_par_casting) > 5 :
                                                        with col6 :
                                                            affiche_film_casting(liste_film_par_casting, 5, liste_casting[1])
         
        st.divider()
        
        liste_film_par_casting = []
        liste_film_par_casting = rech_film_par_cast(liste_casting, 3, df_films)

        st.header('Films avec ' + liste_casting[3])

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1 :
                if len(liste_film_par_casting) > 0 :
                    affiche_film_casting(liste_film_par_casting, 0, liste_casting[2])
                    if len(liste_film_par_casting) > 1 :
                        with col2 :
                            affiche_film_casting(liste_film_par_casting, 1, liste_casting[2])
                            if len(liste_film_par_casting) > 2 :
                                with col3 :
                                    affiche_film_casting(liste_film_par_casting, 2, liste_casting[2])
                                    if len(liste_film_par_casting) > 3 :
                                        with col4 :
                                            affiche_film_casting(liste_film_par_casting, 3, liste_casting[2])
                                            if len(liste_film_par_casting) > 4 :
                                                with col5 :
                                                    affiche_film_casting(liste_film_par_casting, 4, liste_casting[2])
                                                    if len(liste_film_par_casting) > 5 :
                                                        with col6 :
                                                            affiche_film_casting(liste_film_par_casting, 5, liste_casting[2])



    