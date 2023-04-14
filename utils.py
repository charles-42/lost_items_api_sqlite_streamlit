import plotly.express as px
import pandas as pd
from db.import_classes import LostItemImporter, TemperatureImporter
from sqlalchemy import create_engine

def get_importers() -> tuple:
    engine = create_engine('sqlite:///db.sqlite')
    temperature_importer: TemperatureImporter = TemperatureImporter(engine)
    lostitem_importer: LostItemImporter = LostItemImporter(engine)
    return temperature_importer, lostitem_importer
    

def last_update() -> tuple:
    temperature_importer, lostitem_importer = get_importers()
    return temperature_importer._get_last_date(), lostitem_importer._get_last_date()


def update() -> None:
    temperature_importer, lostitem_importer = get_importers()

    temperature_importer.update()
    lostitem_importer.update()


def histogramme(df: pd.DataFrame) -> px.histogram:
    fig: px.histogram = px.histogram(df.groupby(['type_objet', 'date']).size().reset_index(name='count'), x="date", y="count", color="type_objet", histfunc="sum")
    fig.update_traces(xbins_size=604800000) # on regroupe par semaine
    fig.update_layout(width=1000)
    fig.update_layout(bargap=0.1)
    fig.update_xaxes(title="Date où l'objet a été trouvé")
    fig.update_yaxes(title="Nombre d'objets trouvés par semaine")
    return fig


def paris_map(year: str, type_object: str, df_lostitem: pd.DataFrame, df_gare: pd.DataFrame) -> px.scatter_mapbox:
    # Extract year from date and add it to the DataFrame
    df_lostitem['year'] = df_lostitem['date'].str[:4]

    # Filter the DataFrame based on year and object type
    if type_object == "Tous les types":
        df_lostitem_group_year = df_lostitem.groupby(['year', 'nom_gare']).size().reset_index(name='count')
        df_lostitem_filtered = df_lostitem_group_year[(df_lostitem_group_year['year'] == year)]
    else:
        df_lostitem_group_year_type = df_lostitem.groupby(['type_objet', 'year', 'nom_gare']).size().reset_index(name='count')
        df_lostitem_filtered = df_lostitem_group_year_type[(df_lostitem_group_year_type['year'] == year) & (df_lostitem_group_year_type['type_objet'] == type_object)]

    # Merge the two DataFrames
    df = pd.merge(df_gare, df_lostitem_filtered, on='nom_gare', how='inner')

    # Calculate the lost items per million people and round to the nearest integer
    if year in ["2019", "2020", "2021"]:
        year_freq = year
    else:
        year_freq = "2021"
    df["lost_pour_million"] = df["count"] / (df[f'freq_{year_freq}'] / 1000000)
    df["lost_pour_million"] = df["lost_pour_million"].apply(round)
    df = df[["nom_gare", "longitude", "latitude", "lost_pour_million"]]

    # Create a scatter mapbox plot
    fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", size="lost_pour_million", color="lost_pour_million", hover_name="nom_gare", center=dict(lat=48.8566, lon=2.3522), zoom=10, mapbox_style="carto-positron")
    return fig

def scatter_par_type(df_lostitem: pd.DataFrame, df_temp: pd.DataFrame) -> px.scatter:
    # Group the lost items by date and object type and merge with the temperature DataFrame
    df_lostitem_group = df_lostitem[["date", "type_objet"]].groupby(["date", "type_objet"]).size().reset_index(name="count")
    df_merge = pd.merge(df_lostitem_group, df_temp, on='date', how='inner')

    # Create a scatter plot
    fig = px.scatter(df_merge, x="temperature", y="count", color="type_objet", hover_data=['type_objet'], size_max=1)
    fig.update_layout(width=1000)
    fig.update_layout(xaxis_title='Temperature in Celsius', yaxis_title="Number of lost items in a day")
    return fig

def scatter_tous_types(df_lostitem: pd.DataFrame, df_temp: pd.DataFrame) -> px.scatter:
    df_lostitem_group = df_lostitem[["date"]].groupby(["date"]).size().reset_index(name="count")
    df_merge = pd.merge(df_lostitem_group, df_temp, on='date', how='inner')
    fig = px.scatter(df_merge, x="temperature", y="count", size_max=1)
    fig.update_layout(xaxis_title='Température en Celsius', yaxis_title="Nombre d'objets perdus sur une journée ")
    return fig

def saison(date_str: str) -> str:
    mois_jour = date_str[5:]  # extraire le mois et le jour de la date au format string
    
    if mois_jour >= '03-20' and mois_jour <= '06-20':
        return "Printemps"
    elif mois_jour >= '06-21' and mois_jour <= '09-21':
        return "Été"
    elif mois_jour >= '09-22' and mois_jour <= '12-20':
        return "Automne"
    else:
        return "Hiver"

def boxplot(df_lostitem: pd.DataFrame) -> px.box:
    df_lostitem_date = df_lostitem[["date"]].groupby(["date"]).size().reset_index(name="count")
    df_lostitem_date['season'] = df_lostitem_date['date'].apply(saison)

    fig = px.box(data_frame=df_lostitem_date, x="season", y="count")

    # Customize plot
    fig.update_layout(
        xaxis_title="Saison",
        yaxis_title="Nombre d'objets trouvés",
    )
    return fig


def heatmap(df_lostitem: pd.DataFrame) -> px.imshow:
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