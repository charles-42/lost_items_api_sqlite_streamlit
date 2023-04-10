import requests
import logging



def request_stations(station):
    URL = "https://ressources.data.sncf.com/api/records/1.0/search/"
    ressource = "?dataset=frequentation-gares"
    row_limit ="&rows=1"
    station = f"&refine.nom_gare={station}"
    return URL + ressource + row_limit + station



# Set up logging
logging.basicConfig(level=logging.INFO)

station_list = ["Paris Austerlitz","Paris Est", "Paris Gare de Lyon", "Paris Gare du Nord", "Paris Montparnasse", "Paris Saint-Lazare", "Paris Bercy"]




from model import Gare
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


engine = create_engine('sqlite:///db.sqlite')
Session = sessionmaker(bind=engine)
session = Session()

# session.query(Gare).delete()
# session.commit()



for station in station_list:
    station_object = session.get(Gare, station) # On récupère l'objet dans notre BDD
    
    if station == "Paris Bercy":
        station_lib = "Paris Bercy Bourgogne - Pays d'Auvergne"
        my_request = requests.get(request_stations(station_lib))
    else:
        my_request = requests.get(request_stations(station))

    logging.info(f"request réalisée pour {station}")
    
    temp = my_request.json()["records"][0] # Only one row is collected for each station

    station_object.freq_2019 = temp["fields"]["total_voyageurs_non_voyageurs_2019"]+temp["fields"]["total_voyageurs_2019"]
    station_object.freq_2020 = temp["fields"]["total_voyageurs_non_voyageurs_2020"]+temp["fields"]["total_voyageurs_2020"]
    station_object.freq_2021 = temp["fields"]["total_voyageurs_non_voyageurs_2021"]+temp["fields"]["total_voyageurs_2021"]

    session.commit()
