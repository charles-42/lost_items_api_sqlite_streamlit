import requests
import logging
from datetime import datetime
from dateparser import parse
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from .model import LostItem, Temperature
from typing import List, Tuple
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from abc import ABCMeta, abstractmethod  # permet de définir des classes de base


logging.basicConfig(level=logging.INFO)

class Importer(metaclass = ABCMeta):
    
    def __init__(self, engine: Engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()
        self._init_attributes()


    @abstractmethod
    def _init_attributes(self):
        self.TableModel = None
        self.field_list = None


    def _parse_date(self, start_date: str, end_date: str) -> Tuple[datetime, datetime]:
        start_parse = parse(str(start_date))
        end_parse = parse(str(end_date))
        return start_parse, end_parse

    def _get_year_range(self, start_date: str, end_date: str) -> List[Tuple[str, str]]:
        year_ranges = []
        start_parse, end_parse = self._parse_date(start_date,end_date)
        current_year = start_parse.year
        
        while current_year <= end_parse.year:
            year_start = datetime(current_year, 1, 1,1,1,1)
            year_end = datetime(current_year, 12, 31,23,59,59)
            
            if current_year == start_parse.year:
                year_start = start_parse
            if current_year == end_parse.year:
                year_end = end_parse
                
            year_ranges.append((str(year_start.date()), str(year_end.date())))
            current_year += 1
        return year_ranges


    def clean(self) -> None:
        self.session.query(self.TableModel).delete()
        # self.session.query(LostItem).delete()
        self.session.commit()
      
    @abstractmethod
    def import_data(self,x,y):
        pass

    @abstractmethod
    def _create_endpoint(self):
        pass

    def _get_last_date(self) -> str:
        date_string = self.session.query(func.max(LostItem.date)).scalar()
        return str(datetime.fromisoformat(date_string).date())
    
    def update(self)-> None:
        self.import_data(self. _get_last_date(),"now")

    def _insert(self, my_request: requests.Response) -> None:
        for row in my_request.json()["records"]:
                    row_data = {} 
                    for field in self.field_list:
                        try: 
                            row_data[field[0]] = row["fields"][field[1]]
                        except KeyError:
                            row_data[field[0]] = None

                    # self.session.add(LostItem(**temp_data))
                    self.session.add(self.TableModel(**row_data))
        self.session.commit()

class LostItemImporter(Importer):

    station_list = ["Paris Austerlitz", "Paris Est", "Paris Gare de Lyon", "Paris Gare du Nord", "Paris Montparnasse", "Paris Saint-Lazare", "Paris Bercy"]

    def _init_attributes(self):
        self.TableModel= LostItem
        self.field_list = [
        ["date", "date"],
        ["type_objet", "gc_obo_type_c"],
        ["nom_gare", "gc_obo_gare_origine_r_name"],
        ["date_restitution", "gc_obo_date_heure_restitution_c"],
    ]

    def _create_endpoint(self, station: str, start: str, end: str) -> str:
        URL = "https://ressources.data.sncf.com/api/records/1.0/search/"
        ressource = "?dataset=objets-trouves-restitution&q="
        date_fork = f"date%3A%5B{start}+TO+{end}%5D"
        row_limit ="&rows=10000"
        station = f"&refine.gc_obo_gare_origine_r_name={station}"
        endpoint = URL + ressource + date_fork + row_limit + station
        return endpoint.replace(" ", "+")


    def import_data(self, start_date: str, end_date: str) -> None:
        # Set up logging
        
        year_range  = self._get_year_range(start_date,end_date)

        for station in self.station_list:
            for start_date, end_date in year_range:
                
                my_request = requests.get(self._create_endpoint(station, start_date, end_date))

                logging.info(f"REQUETE: {start_date}, {station},{len((my_request.json()['records']))}")

                self._insert(my_request)
                
class TemperatureImporter(Importer):


    def _init_attributes(self):
        self.TableModel= Temperature
        self.field_list = [
            ["date", "date"],
            ["temperature", "tc"],
        ]

    def _create_endpoint(self, start: str, end: str) -> str:
        URL = "https://public.opendatasoft.com/api/records/1.0/search/"
        ressource = "?dataset=donnees-synop-essentielles-omm&q="
        date_fork = f"date%3A%5B{start}+TO+{end}%5D"
        row_limit ="&rows=10000"
        station = f"&refine.nom=ORLY"
        endpoint = URL + ressource + date_fork + row_limit +station
        return endpoint.replace(" ", "+")

        # URL = "https://public.opendatasoft.com/api/records/1.0/search/"
        # ressource = ""
        # row_limit ="&rows=10000"
        # station = f"&refine.nom=ORLY"
        # year_select = f"&refine.date={year}"
        # return URL + ressource + row_limit + station + year_select


    def import_data(self, start_date: str, end_date: str) -> None:
        # Set up logging
        
        year_range  = self._get_year_range(start_date,end_date)

        for start_date, end_date in year_range:

            my_request = requests.get(self._create_endpoint(start_date, end_date))

            logging.info(f"REQUETE: {start_date},{len((my_request.json()['records']))}")

            self._insert(my_request)



if __name__ == "__main__":
    engine = create_engine('sqlite:///db.sqlite')
    my_import = LostItemImporter(engine)
    my_import.clean()
    # my_import.import_by_date("01 january 2018", "now")