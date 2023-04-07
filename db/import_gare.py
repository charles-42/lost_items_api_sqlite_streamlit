import requests
import logging




def request_stations(station):
    URL = "https://ressources.data.sncf.com/api/records/1.0/search/"
    ressource = "?dataset=referentiel-gares-voyageurs"
    row_limit ="&rows=1"
    station = f"&refine.gare_alias_libelle_noncontraint={station}"
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

session.query(Gare).delete()
session.commit()


field_list = [

    ["latitude", "latitude_entreeprincipale_wgs84"],
    ["longitude", "longitude_entreeprincipale_wgs84"],
]

for station in station_list:
    if station == "Paris Bercy":
        station_lib = "Paris Bercy Bourgogne - Pays d'Auvergne"
        my_request = requests.get(request_stations(station_lib))
    else:
        my_request = requests.get(request_stations(station))

    logging.info(f"request réalisée pour {station}")
    
    temp = my_request.json()["records"][0] # Only one row is collected for each station
        
    temp_data= {}

    for field in field_list:
        try: 
            temp_data[field[0]] =temp["fields"][field[1]]
        except KeyError:
            temp_data[field[0]]=None


    session.add(Gare(nom_gare=station,**temp_data))

    session.commit()
