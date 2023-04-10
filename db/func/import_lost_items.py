import requests
import logging
from datetime import datetime
from dateparser import parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import LostItem


def parse_date(start_date, end_date):
    start_parse = parse(str(start_date))
    end_parse = parse(str(end_date))
    return start_parse, end_parse


def get_year_range(start_date, end_date):
    year_ranges = []
    start_date, end_date = parse_date(start_date, end_date)
    current_year = start_date.year
    
    while current_year <= end_date.year:
        year_start = datetime(current_year, 1, 1,1,1,1)
        year_end = datetime(current_year, 12, 31,23,59,59)
        
        if current_year == start_date.year:
            year_start = start_date
        if current_year == end_date.year:
            year_end = end_date
            
        year_ranges.append((str(year_start.date()), str(year_end.date())))
        current_year += 1
    
    return year_ranges


def request_by_year_and_station(station, start, end):
    URL = "https://ressources.data.sncf.com/api/records/1.0/search/"
    ressource = "?dataset=objets-trouves-restitution&q="
    date_fork = f"date%3A%5B{start}+TO+{end}%5D"
    row_limit ="&rows=10000"
    station = f"&refine.gc_obo_gare_origine_r_name={station}"
    endpoint = URL + ressource + date_fork + row_limit + station
    return endpoint.replace(" ", "+")


def import_lost_item(start, end, session):
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    station_list = ["Paris Austerlitz", "Paris Est", "Paris Gare de Lyon", "Paris Gare du Nord", "Paris Montparnasse", "Paris Saint-Lazare", "Paris Bercy"]

    session.query(LostItem).delete()
    session.commit()

    field_list = [
        ["date", "date"],
        ["type_objet", "gc_obo_type_c"],
        ["nom_gare", "gc_obo_gare_origine_r_name"],
        ["date_restitution", "gc_obo_date_heure_restitution_c"],
    ]

    for station in station_list:
        for start_date, end_date in get_year_range(start, end):

            my_request = requests.get(request_by_year_and_station(station, start_date, end_date))

            logging.info(f"request réalisée pour {start_date}, {station},{len((my_request.json()['records']))}")

            for temp in my_request.json()["records"]:
                temp_data = {}

                for field in field_list:
                    try: 
                        temp_data[field[0]] = temp["fields"][field[1]]
                    except KeyError:
                        temp_data[field[0]] = None

                session.add(LostItem(**temp_data))
            session.commit()


if __name__ == "__main__":
    engine = create_engine('sqlite:///db.sqlite')
    Session = sessionmaker(bind=engine)
    session = Session()
    import_lost_item("01 january 2018", "now",session)