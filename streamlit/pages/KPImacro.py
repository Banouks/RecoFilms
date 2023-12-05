import streamlit as st
from st_pages import hide_pages
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import plotly.express as px
from PIL import Image


hide_pages("Details")

chemin = 'pages'

@st.cache_data(ttl=24*60*60)
def readcsv():
    df_full = pd.read_csv(chemin + '/df_full_kpi.csv', sep = ',')
    return df_full

df_full = readcsv()

def image_intro():
    # Affichage de l'image de présentation
    mon_image = Image.open(chemin + '/nuage.png')
    return mon_image

df_full['startYear']=pd.to_datetime(df_full['startYear'])
df_full['release_date']=pd.to_datetime(df_full['release_date'])

@st.cache_data(ttl=24*60*60)
def graph_1() :
    top_film_post_2000 = df_full[['primaryTitle', 'startYear', 'firstGenre', 'revenue', 'budget']]\
                    .loc[(df_full['startYear'].dt.year > 1999) \
                    & (df_full['startYear'].dt.year < 2023) \
                    & (df_full['revenue'] > 1) \
                    & (df_full['budget'] > 1) \
                    & (df_full['release_date'].dt.year > 1)]

    top_film_post_2000['benefice'] = top_film_post_2000['revenue'] - top_film_post_2000['budget']

    top_film_post_2000.drop_duplicates(inplace= True)

    top_film_post_2000 = top_film_post_2000.loc[top_film_post_2000.groupby(df_full.startYear.dt.year)['benefice'].idxmax()]
    
    fig = px.scatter(top_film_post_2000, x= 'startYear', y= 'benefice', color= 'firstGenre', size= 'benefice',\
           labels= {'benefice': "Profit (Millards d'$)", 'startYear': 'Année', 'firstGenre': 'Genre'})
    #fig.update_layout(title= {'text': 'Plus gros bénéfices'})
    fig.update_layout(autosize=False, width=800, height=400)
    st.plotly_chart(fig)

@st.cache_data(ttl=24*60*60)
def graph_2() :
    revenu_post_2000 = df_full[['primaryTitle', 'startYear', 'firstGenre', 'revenue', 'budget']]\
                   .loc[(df_full['startYear'].dt.year > 1999) \
                   & (df_full['startYear'].dt.year < 2023) \
                   & (df_full['revenue'] > 1) \
                   & (df_full['budget'] > 1) \
                   & (df_full['firstGenre'] != r'\N') \
                   & (df_full['release_date'].dt.year > 1)]

    revenu_post_2000['benefice'] = revenu_post_2000['revenue'] - revenu_post_2000['budget']

    revenu_post_2000 = revenu_post_2000[(revenu_post_2000['firstGenre'] != 'Musical') \
                                          & (revenu_post_2000['firstGenre'] != 'History') \
                                            & (revenu_post_2000['firstGenre'] != 'War') \
                                                & (revenu_post_2000['firstGenre'] != 'Adult')]

    revenu_post_2000.drop_duplicates(inplace= True)

    revenu_post_2000 = revenu_post_2000.groupby([revenu_post_2000.startYear.dt.year, revenu_post_2000.firstGenre])['benefice'].sum()
    revenu_post_2000 = revenu_post_2000.reset_index()

    fig = px.area(revenu_post_2000, x= 'startYear', y="benefice", color="firstGenre", \
       labels= {'benefice': "Profit cumulé (Millards d'$)", 'startYear': 'Année', 'firstGenre': 'Genre'})
    #fig.update_layout(title= {'text': 'Evolution des bénéfices par genre'})
    fig.update_layout(autosize=False, width=800, height=400)

    st.plotly_chart(fig)

@st.cache_data(ttl=24*60*60)
def graph_3() :
    note_par_genre_1980 = df_full[['primaryTitle','averageRating', 'firstGenre']]\
                    .loc[(df_full['startYear'].dt.year > 1980) \
                    & (df_full['startYear'].dt.year < 2023) \
                    & (df_full['firstGenre'] != r'\N') \
                    & (df_full['release_date'].dt.year > 1) \
                    & (df_full['numVotes'] > 10000)]

    note_par_genre_1980.drop_duplicates(inplace= True)
    note_par_genre_1980 = note_par_genre_1980[(note_par_genre_1980['firstGenre'] != 'Music') \
                                          & (note_par_genre_1980['firstGenre'] != 'History')]

    fig = px.violin(note_par_genre_1980, x= 'firstGenre', y= 'averageRating', color= 'firstGenre', box= True, \
                labels= {'averageRating': "Notes moyennes", 'firstGenre': 'Genre'})
    #fig.update_layout(title= {'text': 'Dispatch des notes moyennes par genre (+ 10 000 votes)'})
    fig.update_layout(autosize=False, width=800, height=400)

    st.plotly_chart(fig)

@st.cache_data(ttl=24*60*60)
def graph_4() :
    note_par_annee_2000 = df_full[['startYear', 'primaryTitle','averageRating', 'firstGenre', 'numVotes']]\
                    .loc[(df_full['startYear'].dt.year > 1980) \
                    & (df_full['startYear'].dt.year < 2023) \
                    & (df_full['firstGenre'] != r'\N') \
                    & (df_full['release_date'].dt.year > 1)]
                   
    note_par_annee_2000.drop_duplicates(inplace= True)

    note_par_annee_2000 = note_par_annee_2000.groupby([note_par_annee_2000.startYear.dt.year, note_par_annee_2000.firstGenre])['numVotes'].sum()
    note_par_annee_2000 = note_par_annee_2000.reset_index()

    fig = px.line(note_par_annee_2000, x= 'startYear', y="numVotes", color="firstGenre", \
         labels= {'numVotes': "Nombre de votes (Millions)", 'startYear': 'Année', 'firstGenre': 'Genre'})

    #fig.update_layout(title= {'text': 'Evolution du nombre de votes par genre'})
    fig.update_layout(autosize=False, width=800, height=400)

    st.plotly_chart(fig)

@st.cache_data(ttl=24*60*60)
def graph_5() :
    evolution_act = df_full[['startYear', 'primaryName','category']]\
                    .loc[(df_full['startYear'].dt.year > 2012) \
                    & (df_full['startYear'].dt.year < 2023) \
                    & (df_full['firstGenre'] != r'\N') \
                    & (df_full['release_date'].dt.year > 1) \
                    & (df_full['numVotes'] > 10000)]

    evolution_act = evolution_act.loc[(df_full['category'] =='actor') | (df_full['category'] =='actress')]

    evolution_act = evolution_act.groupby([evolution_act.startYear.dt.year, evolution_act.primaryName])['category'].value_counts()
    evolution_act = evolution_act.reset_index()
    evolution_act = evolution_act.groupby([evolution_act.primaryName, evolution_act.category])['count'].sum()
    evolution_act = evolution_act.reset_index()
    evolution_act = evolution_act.sort_values(by= 'count', ascending= False).head(20)

    fig = px.bar_polar(evolution_act, r="count", theta="primaryName", color="category", \
                   color_discrete_sequence= px.colors.qualitative.Pastel1, \
                   labels= {'count': "Nombre d'apparitions", 'primaryName': 'Nom', 'category': 'Metier'})
    #fig.update_layout(title= {'text': "TOP 20 en nombre d'apparitions ces 10 dernières années"})
    fig.update_layout(autosize=False, width=800, height=600)

    st.plotly_chart(fig)


#st.header('Quelques informations intéressantes :')

with st.container():
    st.subheader("Rapport entre le nombre de vote et la note moyenne")
    image = image_intro()
    st.image(image, width= 710)

col1, col2 = st.columns([1, 5])
with col1 :
    checkbox = st.checkbox("Infos :", key= 'graph_6')
with col2 :
    if checkbox :
        st.write("De manière générale plus les utilisateurs votent, meilleures sera la note")
        st.write("Donc un film avec de nombreux votes est fortement recommandable")

st.divider()

with st.container():
    st.subheader("TOP films avec le plus haut revenu par année")
    graph_1()

col1, col2 = st.columns([1, 5])
with col1 :
    checkbox = st.checkbox("Infos :", key= 'graph_1')
with col2 :
    if checkbox :
        st.write("Chaque année, le film top 1 est soit un film d'action soit un film d'aventure")
        st.write("Depuis 2010 les revenus explosent")

st.divider()

with st.container():
    st.subheader("Evolution des revenus par an et par genre")
    graph_2()

col1, col2 = st.columns([1, 5])
with col1 :
    checkbox = st.checkbox("Infos :", key= 'graph_2')
with col2 :
    if checkbox :
        st.write("Les films d'action et les films d'aventure génèrent les plus gros revenus")
        st.write("Effondrement des revenus en 2020 à cause du COVID")

st.divider()

with st.container():
    st.subheader("Violon des notes par genres")
    graph_3()

col1, col2 = st.columns([1, 5])
with col1 :
    checkbox = st.checkbox("Infos :", key= 'graph_3')
with col2 :
    if checkbox :
        st.write("La qualité des films d'animation, les documentaires, biographies et romances se démarquent")

st.divider()

with st.container():
    st.subheader("Evolution du nombre de votes par année")
    graph_4()

col1, col2 = st.columns([1, 5])
with col1 :
    checkbox = st.checkbox("Infos :", key= 'graph_4')
with col2 :
    if checkbox :
        st.write("L'intéret du public se focus principalement sur les films d'action")
        st.write("Encore une fois le COVID à réduit considérablement la fréquentation des salles")

st.divider()

with st.container():
    st.subheader("TOP 20 des apparitions ces 10 dernières années")
    graph_5()

col1, col2 = st.columns([1, 5])
with col1 :
    checkbox = st.checkbox("Infos :", key= 'graph_5')
with col2 :
    if checkbox :
        st.write("Parmis les acteurs-trices les plus populaires les femmes sont sous représentées")
        st.write("La majorité des acteurs-trices vient des USA mais le TOP1 est Indien !")
