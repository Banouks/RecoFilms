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

st.cache_resource.clear()
st.runtime.legacy_caching.clear_cache()

recherche = ''
touslesfilms = []
multiple_films = []
path_image = 'https://image.tmdb.org/t/p/w500'

# Importation des dataframes
df_films = pd.read_csv('./df_films.csv', sep = ',')
df_tmdb = pd.read_csv('./df_tmdb.csv', sep = ',')

# Je remplit les valeurs null
df_films.fillna('None', inplace= True)
df_tmdb.fillna('None', inplace= True)

# Factorization des colonnes str
df_films['original_language'] = df_films['original_language'].factorize()[0]
df_films['firstGenre'] = df_films['firstGenre'].factorize()[0]
df_films['secondGenre'] = df_films['secondGenre'].factorize()[0]

# Normalisation des données avec une échelle permettant de valorisé des colonnes prioritaires
mon_Scaler = MinMaxScaler(feature_range= (0, 30))
df_films[['startYear', 'averageRating', 'numVotes', 'popularity']] = mon_Scaler.fit_transform(df_films[['startYear', 'averageRating', 'numVotes', 'popularity']])                                                                              

# Recherche multi-critères
def recherche_film(des_mots, un_df) :
    
    try : 
        recherche = des_mots.lower().split() #Je place les mots recherchés dans une liste
    
        #Je parcours la liste. Pour chaque mot je recherche dans le df (le df se réduit mot après mot)
        for mot in recherche : 
            un_df = un_df.loc[un_df['originalTitle'].str.lower().\
                              str.contains(mot)][['tconst', 'originalTitle', 'popularity']]
    
        # Je retourne le tconst du film le plus populaire qui contient tous les mots
        return list(un_df.sort_values(by= 'popularity', ascending= False)['tconst'])
    except :
        return print('Aucun film trouvé !')

# Fonction pour ajouter à une checkbox les films trouvés
def multiple_choix(liste_films, df) :
    liste = []
    for film in liste_films :
        liste.append(df[df['tconst'] == film]['originalTitle'].item())
    return liste

# Fonction qui permettra de récupérer automatiquement les paramètres pour le ML
def parametre_film(un_index, un_df):
    
    try :
        #Je récupère les paramètres du film correspondant au tconst récupéré dans la fonction recherche_film
        parametreFilm = un_df[un_df['tconst'] == un_index[0]]\
                        [['original_language', 'startYear', 'firstGenre', 'secondGenre', \
                         'averageRating', 'numVotes', 'popularity']]

        return parametreFilm
    except :
        return print('Aucun film trouvé !')

# Récupère une image à partir d'une URL
def load_image_from_github(url):
  with urllib.request.urlopen(url) as response:
    image = Image.open(response)
  return image

# On va récupérer les plus proches voisins du film recherché
X = df_films[['original_language', 'startYear', 'firstGenre', 'secondGenre', \
            'averageRating', 'numVotes', 'popularity']]

# Apprentissage sur x voisins
filmKNN = NearestNeighbors(n_neighbors= 7).fit(X)

# Affichage de l'image de présentation
image_appli = Image.open('./Chanmel.jpg')
st.image(image_appli, width= 800)
st.write('Welcome back to your Chanmel account you tv shows addict')

recherche = st.text_input('Rechercher un film') # Saisie d'un film par l'utilisateur
if recherche is not None : 
    touslesfilms = recherche_film(recherche, df_films) # Recherche de tous les films comprenant la saisie (tconst)

    multiple_films = multiple_choix(touslesfilms, df_films) # Recherche de tous les films comprenant la saisie (originalTitle)

    # Accrémentation de la chekbox avec les films trouvé
    choix_film = st.selectbox('Voici les films qui correspondent à votre recherche :', multiple_films, )

    # Je fais ma recherche de voisin et j'affiche les résultats (retourne les index)
    ideeFilm = filmKNN.kneighbors(parametre_film(recherche_film(choix_film, df_films), df_films))

    # Récupération des tconst vaec les index des films
    montconst = []
    for item in ideeFilm[1][0][:] :
        montconst.append(df_films.iloc[item]['tconst'])
    # Affichage du film sélectionné
    st.write('Film sélectionné :')
    image_film = load_image_from_github(path_image + df_tmdb[df_tmdb['imdb_id'] == montconst[0]]['poster_path'].item())
    st.image(image_film, width= 200)
    st.write(df_films[df_films['tconst'] == montconst[0]]['originalTitle'].item())

    # JE créé des colonnes pour afficher les images des films voisins
    st.header('Voici nos recommandations')
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1 :
        image_film = load_image_from_github(path_image + df_tmdb[df_tmdb['imdb_id'] == montconst[1]]['poster_path'].item())
        st.image(image_film, width= 200, use_column_width= 'always')
        st.write(df_films[df_films['tconst'] == montconst[1]]['originalTitle'].item())
    with col2 :
        image_film = load_image_from_github(path_image + df_tmdb[df_tmdb['imdb_id'] == montconst[2]]['poster_path'].item())
        st.image(image_film, width= 200, use_column_width= 'always')
        st.write(df_films[df_films['tconst'] == montconst[2]]['originalTitle'].item())
    with col3 :
        image_film = load_image_from_github(path_image + df_tmdb[df_tmdb['imdb_id'] == montconst[3]]['poster_path'].item())
        st.image(image_film, width= 200, use_column_width= 'always')
        st.write(df_films[df_films['tconst'] == montconst[3]]['originalTitle'].item())
    with col4 :
        image_film = load_image_from_github(path_image + df_tmdb[df_tmdb['imdb_id'] == montconst[4]]['poster_path'].item())
        st.image(image_film, width= 200, use_column_width= 'always')
        st.write(df_films[df_films['tconst'] == montconst[4]]['originalTitle'].item())
    with col5 :
        image_film = load_image_from_github(path_image + df_tmdb[df_tmdb['imdb_id'] == montconst[5]]['poster_path'].item())
        st.image(image_film, width= 200, use_column_width= 'always')
        st.write(df_films[df_films['tconst'] == montconst[5]]['originalTitle'].item())
    with col6 :
        image_film = load_image_from_github(path_image + df_tmdb[df_tmdb['imdb_id'] == montconst[6]]['poster_path'].item())
        st.image(image_film, width= 200, use_column_width= 'always')
        st.write(df_films[df_films['tconst'] == montconst[6]]['originalTitle'].item())
    