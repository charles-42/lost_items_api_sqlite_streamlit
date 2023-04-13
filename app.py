import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db.model import Base, Gare, LostItem, Temperature
import matplotlib.pyplot as plt

# créer une connexion à la base de données
engine = create_engine('sqlite:///db.sqlite')
DBSession = sessionmaker(bind=engine)
session = DBSession()

# # Question 1 : Afficher sur un bar-lot plotly la somme du nombre d’objets trouvés par semaine en fonction du type d'objet.

st.header("1-Nombre d'objets trouvés par semaine et par type d'objet à partir de 2018")
with engine.begin() as conn:
    df_lostitem = pd.read_sql(session.query(LostItem).statement, conn)

fig = px.histogram(df_lostitem.groupby(['type_objet','date']).size().reset_index(name='count'), x="date", y="count", color="type_objet",histfunc="sum")
fig.update_traces(xbins_size=604800000) # on regroupe par semaine
fig.update_layout(width=1000)
fig.update_layout(bargap=0.1)
fig.update_xaxes(title="Date où l'objet a été trouvé")
fig.update_yaxes(title="Nombre d'objets trouvés par semaine")

st.plotly_chart(fig)


# Question 2 : A l'aide de plotly, Affichez une carte de Paris avec le nombre d’objets trouvés en fonction de la fréquentation de voyageur de chaque gare. Possibilité de faire varier par année et par type d’objets

st.header("2-Nombre d'objets trouvés pour 1 million d'usagers")

# On laisse la possibilité de choisir l'année et le type d'objet
year = st.selectbox("Choose year", ["2019", "2020", "2021","2022","2023"])
type_list = list(set(df_lostitem['type_objet']))
type_list.insert(0,"Tous les types")
type_object = st.selectbox("Choose object type",type_list)


# On récupère les coordonnées géographiques des gares et leurs fréquentations
with engine.begin() as conn:
    df_gare = pd.read_sql(session.query(Gare).statement, conn)

# On filtre notre base d'objets trouvés en fonction de l'année et du type
df_lostitem['year'] = df_lostitem['date'].str[:4]
if type_object == "Tous les types":
    df_lostitem_group = df_lostitem.groupby(['year','nom_gare']).size().reset_index(name='count')
    df_lostitem_filtered = df_lostitem_group[(df_lostitem_group['year'] == year)]
else:
    df_lostitem_group = df_lostitem.groupby(['type_objet','year','nom_gare']).size().reset_index(name='count')
    df_lostitem_filtered = df_lostitem_group[(df_lostitem_group['year'] == year)  & (df_lostitem_group['type_objet'] == type_object)]

# On rassemble des deux df
df_frequetation = pd.merge(df_gare, df_lostitem_filtered, on='nom_gare', how='inner')

# On calcul le ratio de fréquentation en projettant les valeur de 2021 sur 2022 et 2023
if year in ["2019", "2020", "2021"]:
    year_freq = year
else:
    year_freq="2021"
df_frequetation["lost_pour_million"] = df_frequetation["count"]/(df_frequetation[f'freq_{year_freq}']/1000000)
df_frequetation["lost_pour_million"] = df_frequetation["lost_pour_million"].apply(round)
df_frequetation = df_frequetation[["nom_gare",	"longitude","latitude","lost_pour_million"]]


fig = px.scatter_mapbox(df_frequetation, lat="latitude", lon="longitude", size="lost_pour_million", color="lost_pour_million", hover_name="nom_gare", center=dict(lat=48.8566, lon=2.3522), zoom=10, mapbox_style="carto-positron")
st.plotly_chart(fig)

# Question 3 : Afficher à l'aide de seaborn le nombre d’objets trouvés par jour en fonction de la température sur un scatterplot.

st.header("3-Nombre d'objets trouvés sur une journée en fonction de la température")

with engine.begin() as conn:
    df_temp = pd.read_sql(session.query(Temperature).statement, conn)

type_selector = st.selectbox("", ["Tous les types d'objet","Type par type"])


if type_selector ==  "Type par type":
    df_lostitem_group = df_lostitem[["date","type_objet"]].groupby(["date","type_objet"]).size().reset_index(name="count")
    df_merge = pd.merge(df_lostitem_group, df_temp, on='date', how='inner')
    fig = px.scatter(df_merge, x="temperature", y="count", color="type_objet",hover_data=['type_objet'], size_max=1)
    fig.update_layout(width=1000)
else:
    df_lostitem_group = df_lostitem[["date"]].groupby(["date"]).size().reset_index(name="count")
    df_merge = pd.merge(df_lostitem_group, df_temp, on='date', how='inner')
    fig = px.scatter(df_merge, x="temperature", y="count", size_max=1)


fig.update_layout(xaxis_title='Température en Celsius', yaxis_title="Nombre d'objets perdus sur une journée ")
st.plotly_chart(fig)
# show the plot

# Question 4: Affichez un box-plot du nombre d'objet perdu par jour en fonction de la saison (été, automne, printemps, hiver).

st.header("4-Nombre d'objets trouvés en fonction de la saison, tous types d'objet confondus")


def saison(date_str):
    mois_jour = date_str[5:]  # extraire le mois et le jour de la date au format string
    
    if mois_jour >= '03-20' and mois_jour <= '06-20':
        return "Printemps"
    elif mois_jour >= '06-21' and mois_jour <= '09-21':
        return "Été"
    elif mois_jour >= '09-22' and mois_jour <= '12-20':
        return "Automne"
    else:
        return "Hiver"

df_lostitem_date = df_lostitem[["date"]].groupby(["date"]).size().reset_index(name="count")
df_lostitem_date['season'] = df_lostitem_date['date'].apply(saison)

fig = px.box(data_frame=df_lostitem_date, x="season", y="count")

# Customize plot
fig.update_layout(
    xaxis_title="Saison",
    yaxis_title="Nombre d'objets trouvés",
)
st.plotly_chart(fig)


# Question 5: Affichez le nombre d'objets trouvés médian par jour en fonction du type d'objet et de la saison sur une heatmap.
st.header("5-Nombre d'objets trouvés en fonction de la saison et du type d'objet")


df_lostitem_group = df_lostitem[["date","type_objet"]].groupby(["date","type_objet"]).size().reset_index(name="count")
    

df_lostitem_group['season'] = df_lostitem_group['date'].apply(saison)

df_med = df_lostitem_group[["season","type_objet","count"]].groupby(["season","type_objet"]).median().reset_index()
new_df = df_med.pivot(index='type_objet', columns='season')['count'].fillna(0)
fig = px.imshow(new_df, x=new_df.columns, y=new_df.index, color_continuous_scale="Reds")
# fig = px.imshow(img = df_lostitem_group[["season","type_objet","count"]], x="season", y="type_objet", color_continuous_scale="Reds")
# Customize plot
fig.update_layout(
    xaxis_title= "Saison",
    yaxis_title=  "Type d'objets trouvés",
)
st.plotly_chart(fig)