import requests
import logging




def request_by_year_and_station(year,station):
    URL = "https://ressources.data.sncf.com/api/records/1.0/search/"
    ressource = "?dataset=objets-trouves-restitution&q=&sort=date"
    row_limit ="&rows=10000"
    year = f"&refine.date={year}"
    station = f"&refine.gc_obo_gare_origine_r_name={station}"
    return URL + ressource + row_limit + year + station

# Set up logging
logging.basicConfig(level=logging.INFO)

station_list = ["Paris Austerlitz","Paris Est", "Paris Gare de Lyon", "Paris Gare du Nord", "Paris Montparnasse", "Paris Saint-Lazare", "Paris Bercy"]





from model import LostItem
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


engine = create_engine('sqlite:///db.sqlite')
Session = sessionmaker(bind=engine)
session = Session()

session.query(LostItem).delete()
session.commit()

field_list = [
    ["date", "date"],
    ["type_objet", "gc_obo_type_c"],
    ["nom_gare", "gc_obo_gare_origine_r_name"],
    ["date_restitution", "gc_obo_date_heure_restitution_c"],
]

for station in station_list:
    for year in [2019,2020,2021,2022]:
        my_request = requests.get(request_by_year_and_station(year,station))
        logging.info(f"request réalisée pour , {year}, {station}")
        for temp in my_request.json()["records"]:
            
            temp_data= {}

            for field in field_list:
                try: 
                    temp_data[field[0]] =temp["fields"][field[1]]
                except KeyError:
                    temp_data[field[0]]=None


            session.add(LostItem(**temp_data))
        session.commit()
