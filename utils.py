import plotly.express as px
import pandas as pd

def histogramme(df):
    fig = px.histogram(df.groupby(['type_objet','date']).size().reset_index(name='count'), x="date", y="count", color="type_objet",histfunc="sum")
    fig.update_traces(xbins_size=604800000) # on regroupe par semaine
    fig.update_layout(width=1000)
    fig.update_layout(bargap=0.1)
    fig.update_xaxes(title="Date où l'objet a été trouvé")
    fig.update_yaxes(title="Nombre d'objets trouvés par semaine")
    return fig

def paris_map(year,type_object,df_lostitem,df_gare):
    
    df_lostitem['year'] = df_lostitem['date'].str[:4]

    # On filtre notre base d'objets trouvés en fonction de l'année et du type

    if type_object == "Tous les types":
        df_lostitem_group_year= df_lostitem.groupby(['year','nom_gare']).size().reset_index(name='count')
        df_lostitem_filtered = df_lostitem_group_year[(df_lostitem_group_year['year'] == year)]
    else:
        df_lostitem_group_year_type = df_lostitem.groupby(['type_objet','year','nom_gare']).size().reset_index(name='count')
        df_lostitem_filtered = df_lostitem_group_year_type[(df_lostitem_group_year_type['year'] == year)  & (df_lostitem_group_year_type['type_objet'] == type_object)]

    # On rassemble des deux df
    df = pd.merge(df_gare, df_lostitem_filtered, on='nom_gare', how='inner')
        
    # On calcul le ratio de fréquentation en projettant les valeur de 2021 sur 2022 et 2023
    if year in ["2019", "2020", "2021"]:
        year_freq = year
    else:
        year_freq="2021"
    df["lost_pour_million"] = df["count"]/(df[f'freq_{year_freq}']/1000000)
    df["lost_pour_million"] = df["lost_pour_million"].apply(round)
    df = df[["nom_gare",	"longitude","latitude","lost_pour_million"]]

    fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", size="lost_pour_million", color="lost_pour_million", hover_name="nom_gare", center=dict(lat=48.8566, lon=2.3522), zoom=10, mapbox_style="carto-positron")
    return fig

def scatter_par_type(df_lostitem,df_temp):
    df_lostitem_group = df_lostitem[["date","type_objet"]].groupby(["date","type_objet"]).size().reset_index(name="count")
    df_merge = pd.merge(df_lostitem_group, df_temp, on='date', how='inner')
    fig = px.scatter(df_merge, x="temperature", y="count", color="type_objet",hover_data=['type_objet'], size_max=1)
    fig.update_layout(width=1000)
    fig.update_layout(xaxis_title='Température en Celsius', yaxis_title="Nombre d'objets perdus sur une journée ")
    return fig

def scatter_tous_types(df_lostitem,df_temp):
    df_lostitem_group = df_lostitem[["date"]].groupby(["date"]).size().reset_index(name="count")
    df_merge = pd.merge(df_lostitem_group, df_temp, on='date', how='inner')
    fig = px.scatter(df_merge, x="temperature", y="count", size_max=1)
    fig.update_layout(xaxis_title='Température en Celsius', yaxis_title="Nombre d'objets perdus sur une journée ")
    return fig

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

def boxplot(df_lostitem):
    df_lostitem_date = df_lostitem[["date"]].groupby(["date"]).size().reset_index(name="count")
    df_lostitem_date['season'] = df_lostitem_date['date'].apply(saison)

    fig = px.box(data_frame=df_lostitem_date, x="season", y="count")

    # Customize plot
    fig.update_layout(
        xaxis_title="Saison",
        yaxis_title="Nombre d'objets trouvés",
    )
    return fig


def heatmap(df_lostitem):
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
    return fig