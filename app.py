import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db.model import Base, Gare, LostItem, Temperature

# créer une connexion à la base de données
engine = create_engine('sqlite:///db.sqlite')
DBSession = sessionmaker(bind=engine)
session = DBSession()

# # Question 1 : Afficher sur un bar-lot plotly la somme du nombre d’objets trouvés par semaine en fonction du type d'objet.

st.header("Nombre d'objets trouvés par semaine et par type d'objet à partir de 2018")
with engine.begin() as conn:
    df = pd.read_sql(session.query(LostItem).statement, conn)

fig = px.histogram(df.groupby(['type_objet','date']).size().reset_index(name='count'), x="date", y="count", color="type_objet",histfunc="sum")
fig.update_traces(xbins_size=604800000) # on regroupe par semaine
fig.update_layout(width=1100)
fig.update_layout(bargap=0.1)
fig.update_xaxes(title="Date ou l'objet a été trouvé")
fig.update_yaxes(title="Nombre d'objets trouvés par semaine")

st.plotly_chart(fig)


# Question 2 : A l'aide de plotly, Affichez une carte de Paris avec le nombre d’objets trouvés en fonction de la fréquentation de voyageur de chaque gare. Possibilité de faire varier par année et par type d’objets

st.header("Question 2")

year = st.selectbox("Choose year", ["2019", "2020", "2021","2022","2023"])
type_list = list(set(df['type_objet']))
type_list.append("Tous les types")
type_object = st.selectbox("Choose object type",type_list)

# year = 2021
# type_object = 'Tous les types'

with engine.begin() as conn:
    df_gare = pd.read_sql(session.query(Gare).statement, conn)

df['year'] = pd.to_datetime(df['date'], format='%Y-%m-%d').dt.year

if type_object == "Tous les types":
    df_group = df.groupby(['year','nom_gare']).size().reset_index(name='count')
    filtered_df = df_group[(df_group['year'] == year)]
else:
    df_group = df.groupby(['type_objet','year','nom_gare']).size().reset_index(name='count')
    filtered_df = df_group[(df_group['year'] == year)  & (df_group['type_objet'] == type_object)]

merged_df = pd.merge(df_gare, filtered_df, on='nom_gare', how='inner')

if year in [2019, 2020, 2021]:
    year_freq = year
else:
    year_freq=2021

merged_df["lost_pour_million"] = merged_df["count"]/(merged_df[f'freq_{year_freq}']/1000000)
df_final = merged_df[["nom_gare",	"longitude",	"latitude","lost_pour_million"]]

fig = px.scatter_mapbox(df_final, lat="latitude", lon="longitude", size="lost_pour_million", color="lost_pour_million", hover_name="nom_gare", center=dict(lat=48.8566, lon=2.3522), zoom=10, mapbox_style="carto-positron")
st.plotly_chart(fig)