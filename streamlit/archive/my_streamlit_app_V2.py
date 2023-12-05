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

recherche = ''
touslesfilms = []
multiple_films = []
path_image = 'https://image.tmdb.org/t/p/w500'

# Importation des dataframes
@st.cache_data(ttl=24*60*60)
#@st.cache(ttl=24*60*60)
def readcsv():
    df1 = pd.read_csv('./df_films.csv', sep = ',')
    return df1

df_films = readcsv()
    
# Je remplit les valeurs null
df_films.fillna('None', inplace= True)

# Factorization des colonnes str
df_films['original_language'] = df_films['original_language'].factorize()[0]
df_films['firstGenre'] = df_films['firstGenre'].factorize()[0]
df_films['secondGenre'] = df_films['secondGenre'].factorize()[0]

# Normalisation des données avec une échelle permettant de valorisé des colonnes prioritaires
mon_Scaler = MinMaxScaler(feature_range= (0, 30))
df_films[['startYear', 'averageRating', 'numVotes', 'popularity']] = mon_Scaler.fit_transform(df_films[['startYear', 'averageRating', 'numVotes', 'popularity']])                                                                              

# Recherche films multi-critères
def recherche_film(des_mots, un_df) :
    
    try : 
        recherche = des_mots.lower().split() #Je place les mots recherchés dans une liste
    
        #Je parcours la liste. Pour chaque mot je recherche dans le df (le df se réduit mot après mot)
        for mot in recherche : 
            un_df = un_df.loc[un_df['originalTitle_Year'].str.lower().\
                              str.contains(mot)][['tconst', 'originalTitle_Year', 'popularity']]
    
        # Je retourne les tconst du film le plus populaire qui contient tous les mots
        return list(un_df.sort_values(by= 'popularity', ascending= False)['tconst'])
    except :
        return print('Aucun film trouvé !')

# Fonction pour ajouter à une checkbox les films trouvés
def multiple_choix(liste_films, df) :
    liste = []
    for film in liste_films :
        liste.append(df[df['tconst'] == film]['originalTitle_Year'].item())
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

# Recherche du casting correspondant à un film en fonction du tcont du film / renvoi la liste du casting
def recherche_casting(un_id, un_df):
    # Récupération du casting dans une liste en spératant les personnes
    récuperation = un_df[un_df['tconst'] == un_id]['primaryName']\
        .apply(lambda x : x.split(sep=','))
    # Transformation en liste
    liste = récuperation.iloc[0]
    # Limitation aux 3 1eere personnes
    if len(liste) > 4 :
        liste = liste[:4]
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

@st.cache_data(ttl=24*60*60)
#@st.cache_resource
def mlKNN():
    # On va récupérer les plus proches voisins du film recherché
    X = df_films[['original_language', 'startYear', 'firstGenre', 'secondGenre', \
            'averageRating', 'numVotes', 'popularity']]

    # Apprentissage sur x voisins
    entrainement = NearestNeighbors(n_neighbors= 13).fit(X)
    return entrainement

filmKNN = mlKNN()

@st.cache_data(ttl=24*60*60)
#@st.cache(ttl=24*60*60)
def image_intro():
    # Affichage de l'image de présentation
    mon_image = Image.open('./Chanmel.jpg')
    return mon_image

image = image_intro()
st.image(image, width= 800)

st.write('Welcome back to your Chanmel account you tv shows addict')

recherche = st.text_input('Rechercher un film :') # Saisie d'un film par l'utilisateur
if recherche : 
    touslesfilms = recherche_film(recherche, df_films) # Recherche de tous les films comprenant la saisie (tconst)

    multiple_films = multiple_choix(touslesfilms, df_films) # Recherche de tous les films comprenant la saisie (originalTitle)

    # Accrémentation de la chekbox avec les films trouvé
    choix_film = st.selectbox('Voici les films qui correspondent à votre recherche :', multiple_films)
    
    if choix_film :
        st.divider()

        tconst_film = recherche_film(choix_film, df_films)

        # Je fais ma recherche de voisin et j'affiche les résultats (retourne les index)
        ideeFilm = filmKNN.kneighbors(parametre_film(tconst_film, df_films))

        # Récupération des tconst vaec les index des films
        montconst = []
        for item in ideeFilm[1][0][:] :
             montconst.append(df_films.iloc[item]['tconst'])

        # Affichage du film sélectionné
        st.write('Film sélectionné :')
        try : 
            image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == montconst[0]]['poster_path'].item())
        except : 
            image_film = Image.open('./image-non-disponible.png')
        st.image(image_film, width= 200)
        st.write(df_films[df_films['tconst'] == montconst[0]]['originalTitle'].item())

        st.divider()
    
        # Je crée des colonnes pour afficher les images des films voisins
        st.header('Voici nos recommandations')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1 :
            try :
                 image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == montconst[1]]['poster_path'].item())
            except : 
                 image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == montconst[1]]['originalTitle'].item())
        with col2 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == montconst[2]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == montconst[2]]['originalTitle'].item())
        with col3 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == montconst[3]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == montconst[3]]['originalTitle'].item())
        with col4 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == montconst[4]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == montconst[4]]['originalTitle'].item())
        with col5 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == montconst[5]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == montconst[5]]['originalTitle'].item())
        with col6 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == montconst[6]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == montconst[6]]['originalTitle'].item())

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1 :
            try :
                 image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == montconst[7]]['poster_path'].item())
            except : 
                 image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == montconst[7]]['originalTitle'].item())
        with col2 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == montconst[8]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == montconst[8]]['originalTitle'].item())
        with col3 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == montconst[9]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == montconst[9]]['originalTitle'].item())
        with col4 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == montconst[10]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == montconst[10]]['originalTitle'].item())
        with col5 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == montconst[11]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == montconst[11]]['originalTitle'].item())
        with col6 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == montconst[12]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == montconst[12]]['originalTitle'].item())
        
        st.divider()

        liste_casting = recherche_casting(montconst[0], df_films)

        liste_film_par_casting = rech_film_par_cast(liste_casting, 1, df_films)

        st.header('Films avec ' + liste_casting[1])

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1 :
            try :
                 image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == liste_film_par_casting[0]]['poster_path'].item())
            except : 
                 image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == liste_film_par_casting[0]]['originalTitle'].item())
        with col2 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == liste_film_par_casting[1]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == liste_film_par_casting[1]]['originalTitle'].item())
        with col3 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == liste_film_par_casting[2]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == liste_film_par_casting[2]]['originalTitle'].item())
        with col4 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == liste_film_par_casting[3]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == liste_film_par_casting[3]]['originalTitle'].item())
        with col5 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == liste_film_par_casting[4]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == liste_film_par_casting[4]]['originalTitle'].item())
        with col6 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == liste_film_par_casting[5]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == liste_film_par_casting[5]]['originalTitle'].item())
         
        st.divider()
        
        liste_film_par_casting = rech_film_par_cast(liste_casting, 2    , df_films)

        st.header('Films avec ' + liste_casting[2])

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1 :
            try :
                 image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == liste_film_par_casting[0]]['poster_path'].item())
            except : 
                 image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == liste_film_par_casting[0]]['originalTitle'].item())
        with col2 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == liste_film_par_casting[1]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == liste_film_par_casting[1]]['originalTitle'].item())
        with col3 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == liste_film_par_casting[2]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == liste_film_par_casting[2]]['originalTitle'].item())
        with col4 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == liste_film_par_casting[3]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == liste_film_par_casting[3]]['originalTitle'].item())
        with col5 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == liste_film_par_casting[4]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == liste_film_par_casting[4]]['originalTitle'].item())
        with col6 :
            try :
                image_film = load_image_from_github(path_image + df_films[df_films['tconst'] == liste_film_par_casting[5]]['poster_path'].item())
            except : 
                image_film = Image.open('./image-non-disponible.png')
            st.image(image_film, width= 200, use_column_width= 'always')
            st.write(df_films[df_films['tconst'] == liste_film_par_casting[5]]['originalTitle'].item())



    