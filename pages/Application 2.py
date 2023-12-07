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
@st.cache_resource(max_entries= 1)
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
#df_films, df_tmdb = readcsv()
    
# Je remplit les valeurs null
df_films.fillna('None', inplace= True)

# remplace les e, a, o
def remplacer(phrase):
    accentse = ['é', 'è', 'ê', 'ë']
    accentsa = ['à', 'ä', 'â']
    accentso = ['Ô', 'ö']
    for i in accentse:
        phrase = phrase.replace(i, 'e')
    for i in accentsa:
        phrase = phrase.replace(i, 'a')
    for i in accentso:
        phrase = phrase.replace(i, 'o')
    return phrase

# Recherche films multi-critères
def recherche_film(des_mots, un_df) :

        interdit = '?!/:.;=+)([{"&@-_`*"`*^¨§<>}])'
        for i in interdit :
            if i in des_mots :
                des_mots = des_mots.replace(i,'')

        des_mots =  remplacer(des_mots) #remplacement des lettres accentuées
        recherche = des_mots.lower().split() #Je place les mots recherchés dans une liste
        liste_films = df_films['originalTitle_Year'].to_list() #Liste de tous les films du df
        
        #Je parcours la liste. Pour chaque mot je recherche dans la liste. Elle se réduit au fur est à mesure
        for mot in recherche : 
            liste_films = [film for film \
                        in liste_films \
                        if mot \
                        in remplacer(film)\
                        .lower()]

        #df vide pour intégrer les films trouvés dans la recherche
        df = pd.DataFrame(columns= ['tconst', 'originalTitle_Year', 'popularity'])

        #accrémentation du df avec tous les films trouvés
        for film in liste_films :
            df = pd.concat([df,un_df.loc[un_df['originalTitle_Year'] == film][['tconst', 'originalTitle_Year', 'popularity']]])
       
        # Je retourne les tconst du film le plus populaire qui contient tous les mots
        return list(df.sort_values(by= 'popularity', ascending= False)['tconst'])

# Fonction pour ajouter à une checkbox les films trouvés
def multiple_choix(liste_films, df) :
    liste = []
    for film in liste_films :
        liste.append(df[df['tconst'] == film]['originalTitle_Year'].item())
    return liste

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

@st.cache_data
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

# affiche tous les films recommandés en fonction du titre
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

# affiche tous les films recommandés en fonction du casting
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

def submit_text():
    st.session_state.recherche = st.session_state.text

def submit_select():
    st.session_state.choix_film = st.session_state.select

filmKNN = mlKNN()

@st.cache_data
def image_intro():
    # Affichage de l'image de présentation
    mon_image = Image.open(chemin + '/Chanmel 2.jpg')
    return mon_image

image = image_intro()
st.image(image, width= 800, use_column_width= 'always')

st.write('Welcome back to your Chanmel account you tv shows addict')

if 'recherche' not in st.session_state :
    recherche = st.text_input('Rechercher un film 👇 :', placeholder= 'Ecrivez ici', key= 'text', on_change=submit_text) # Saisie d'un film par l'utilisateur
else : 
    recherche = st.text_input('Rechercher un film 👇 :', placeholder= 'Ecrivez ici', value= st.session_state.recherche, \
                               key= 'text', on_change=submit_text) # Saisie d'un film par l'utilisateur

if recherche : 

    touslesfilms = recherche_film(recherche, df_films) # Recherche de tous les films comprenant la saisie (tconst)
    #st.write(touslesfilms) 
    if len(touslesfilms) > 0 :

        multiple_films = multiple_choix(touslesfilms, df_films) # Recherche de tous les films comprenant la saisie (originalTitle)
        #st.write(multiple_films)  
        # Accrémentation de la chekbox avec les films trouvé    
        if 'choix_film' not in st.session_state :
            choix_film = st.selectbox('Voici les films qui correspondent à votre recherche :', multiple_films, key= 'select', \
                                       on_change= submit_select)
            #st.session_state.choix_film = choix_film
        else :
            choix_film = st.session_state.choix_film
            #st.write('choix_film ' + choix_film)
            if choix_film in multiple_films :
                choix_film = st.selectbox('Voici les films qui correspondent à votre recherche :', multiple_films, index= multiple_films.index(choix_film), \
                                           key= 'select', on_change= submit_select)
                #st.write('choix_film ' + choix_film)
            else :
                choix_film = st.selectbox('Voici les films qui correspondent à votre recherche :', multiple_films, key= 'select', on_change= submit_select)
            #st.write('choix_film ' + choix_film)
            #st.session_state.choix_film = choix_film
    
        if choix_film :
            #st.session_state.choix_film = choix_film
            st.divider()

            tconst_film = recherche_film(choix_film, df_films)

            # Je fais ma recherche de voisin et j'affiche les résultats (retourne les index)
            ideeFilm = filmKNN.kneighbors(parametre_film(tconst_film, df_films))

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
            st.write("Cliquez sur le film de votre choix 👇")

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
            st.write("Cliquez sur le film de votre choix 👇")
        
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
            st.write("Cliquez sur le film de votre choix 👇")
        
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
            st.write("Cliquez sur le film de votre choix 👇")

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



    