import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db.model import Base, Gare, LostItem, Temperature
import matplotlib.pyplot as plt
from utils import histogramme, paris_map, scatter_par_type, scatter_tous_types, boxplot, heatmap

# créer une connexion à la base de données
engine = create_engine('sqlite:///db.sqlite')
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Importation des données
with engine.begin() as conn:
    df_lostitem = pd.read_sql(session.query(LostItem).statement, conn)

with engine.begin() as conn:
    df_gare = pd.read_sql(session.query(Gare).statement, conn)

with engine.begin() as conn:
    df_temp = pd.read_sql(session.query(Temperature).statement, conn)
####################################################################
###### Question 1 : Afficher sur un histogramme plotly la somme du nombre d’objets trouvés par semaine en fonction du type d'objet.
####################################################################
st.header("1-Nombre d'objets trouvés par semaine et par type d'objet à partir de 2018")

st.plotly_chart(histogramme(df_lostitem))

####################################################################
###### Question 2 : A l'aide de plotly, Affichez une carte de Paris avec le nombre d’objets trouvés en fonction de la fréquentation de voyageur de chaque gare. Possibilité de faire varier par année et par type d’objets
####################################################################

st.header("2-Nombre d'objets trouvés pour 1 million d'usagers")

######### SELECT BOX [year,type_list ] #########
year = st.selectbox("Choose year", ["2019", "2020", "2021","2022","2023"])
type_list = list(set(df_lostitem['type_objet']))
type_list.insert(0,"Tous les types")
type_object = st.selectbox("Choose object type",type_list)

######### FIGURE #########
st.plotly_chart(paris_map(year,type_object, df_lostitem,df_gare ))

####################################################################
#### Question 3 : Afficher à l'aide de seaborn le nombre d’objets trouvés par jour en fonction de la température sur un scatterplot.
####################################################################
st.header("3-Nombre d'objets trouvés sur une journée en fonction de la température")

######### SELECT BOX [type] #########
type_selector = st.selectbox("", ["Tous les types d'objet","Type par type"])

######### FIGURE #########
if type_selector ==  "Type par type":
    st.plotly_chart(scatter_par_type(df_lostitem,df_temp))
else:
    st.plotly_chart(scatter_tous_types(df_lostitem,df_temp))


####################################################################
####### Question 4: Affichez un box-plot du nombre d'objet perdu par jour en fonction de la saison (été, automne, printemps, hiver).
####################################################################
st.header("4-Nombre d'objets trouvés en fonction de la saison, tous types d'objet confondus")

st.plotly_chart(boxplot(df_lostitem))

####################################################################
####### Question 5: Affichez le nombre d'objets trouvés médian par jour en fonction du type d'objet et de la saison sur une heatmap.
####################################################################

st.header("5-Nombre d'objets trouvés en fonction de la saison et du type d'objet")

st.plotly_chart(heatmap(df_lostitem))