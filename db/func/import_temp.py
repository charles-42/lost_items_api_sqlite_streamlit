

import requests
import logging



def request_temp(year):
    URL = "https://public.opendatasoft.com/api/records/1.0/search/"
    ressource = "?dataset=donnees-synop-essentielles-omm"
    row_limit ="&rows=10000"
    station = f"&refine.nom=ORLY"
    year_select = f"&refine.date={year}"
    return URL + ressource + row_limit + station + year_select

# Set up logging
logging.basicConfig(level=logging.INFO)




from model import TemperatureHeure
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


engine = create_engine('sqlite:///db.sqlite')
Session = sessionmaker(bind=engine)
session = Session()

session.query(TemperatureHeure).delete()
session.commit()


field_list = [

    ["date", "date"],
    ["temperature", "tc"],
]

for year in range(2019,2023):

    my_request = requests.get(request_temp(year))

    logging.info(f"request réalisée pour {year}")
    for temp in my_request.json()["records"]:

            
        temp_data= {}

        for field in field_list:
            try: 
                temp_data[field[0]] =temp["fields"][field[1]]
            except KeyError:
                temp_data[field[0]]=None


        session.add(TemperatureHeure(**temp_data))

        session.commit()
