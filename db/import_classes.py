import requests
import logging
from datetime import datetime
from dateparser import parse
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from .model import LostItem, Temperature, Gare
from typing import List, Tuple
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from abc import ABCMeta, abstractmethod  # permet de définir des classes de base
import pandas as pd


logging.basicConfig(level=logging.INFO)

class Importer(metaclass = ABCMeta):
    
    def __init__(self, engine: Engine):
        """
            Initializes a new Importer instance.

            Args:
                engine (sqlalchemy.engine.Engine): The SQLAlchemy database engine to use.
        """
        self.engine = engine
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()
        self._init_attributes()


    @abstractmethod
    def _init_attributes(self):
        """
        Initializes the attributes needed for the Importer instance.

        This method should set the `TableModel` and `field_list` attributes.
        """
        self.TableModel = None
        self.field_list = None


    def _parse_date(self, start_date: str, end_date: str) -> Tuple[datetime, datetime]:
        """
        Parses the start and end dates into datetime objects.

        Args:
        start_date (str): The start date in ISO format (yyyy-mm-dd).
        end_date (str): The end date in ISO format (yyyy-mm-dd).

        Returns:
        Tuple[datetime, datetime]: A tuple containing the start and end dates as datetime objects.
        """
        start_parse = parse(str(start_date))
        end_parse = parse(str(end_date))
        return start_parse, end_parse

    def _get_year_range(self, start_date: str, end_date: str) -> List[Tuple[str, str]]:
        """
        Gets a list of year ranges based on the start and end dates.

        Args:
        start_date (str): The start date in ISO format (yyyy-mm-dd).
        end_date (str): The end date in ISO format (yyyy-mm-dd).

        Returns:
        List[Tuple[str, str]]: A list of year ranges represented as tuples of (start_date, end_date).
        """
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
        """
        Cleans the database by deleting all records from the TableModel.
        """
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
        """
        Private method that retrieves the last date from the database and returns it as a string.

        Returns:
            str: Last date as a string in the format 'YYYY-MM-DD'.
        """
        date_string = self.session.query(func.max(LostItem.date)).scalar()
        return str(datetime.fromisoformat(date_string).date())
    
    def update(self)-> None:
        """
        Public method that updates the database by importing new data. It retrieves the last date from the database
        and imports data from that date up to the current date.
        
        Returns:
            None.
        """
        self.import_data(self. _get_last_date(),"now")

    def _insert(self, my_request: requests.Response) -> None:
        """
        Private method that inserts data into the database from a given requests.Response object.

        Args:
            my_request (requests.Response): The Response object containing the data to be inserted.

        Returns:
            None.
        """
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
    
    """
    A class for importing lost item data from the SNCF API and storing it in a database.

    Attributes:
    -----------
    station_list : List[str]
        A list of train stations to search for lost items.
    TableModel : model class
        The database model class to be used for storing the imported data.
    field_list : List[List[str, str]]
        A list of fields to be extracted from the API response and their corresponding database columns.

    Methods:
    --------
    _init_attributes():
        Initializes the class attributes.
    _create_endpoint(station: str, start: str, end: str) -> str:
        Creates the API endpoint URL for a given station, start date, and end date.
    import_data(start_date: str, end_date: str) -> None:
        Imports lost item data from the SNCF API for a given date range and saves it to the database.
    """

    station_list = ["Paris Austerlitz", "Paris Est", "Paris Gare de Lyon", "Paris Gare du Nord", "Paris Montparnasse", "Paris Saint-Lazare", "Paris Bercy"]

    def _init_attributes(self):
        """
        Initializes the class attributes.
        """

        self.TableModel= LostItem
        self.field_list = [
        ["date", "date"],
        ["type_objet", "gc_obo_type_c"],
        ["nom_gare", "gc_obo_gare_origine_r_name"],
        ["date_restitution", "gc_obo_date_heure_restitution_c"],
    ]

    def _create_endpoint(self, station: str, start: str, end: str) -> str:
        """
        Creates the API endpoint URL for a given station, start date, and end date.

        Parameters:
        -----------
        station : str
            The train station to search for lost items.
        start : str
            The start date for the API query in the format "YYYY-MM-DD".
        end : str
            The end date for the API query in the format "YYYY-MM-DD".

        Returns:
        --------
        endpoint : str
            The URL endpoint for the API query.
        """
                
        URL = "https://ressources.data.sncf.com/api/records/1.0/search/"
        ressource = "?dataset=objets-trouves-restitution&q="
        date_fork = f"date%3A%5B{start}+TO+{end}%5D"
        row_limit ="&rows=10000"
        station = f"&refine.gc_obo_gare_origine_r_name={station}"
        endpoint = URL + ressource + date_fork + row_limit + station
        return endpoint.replace(" ", "+")


    def import_data(self, start_date: str, end_date: str) -> None:
        """
        Imports lost item data from the SNCF API for a given date range and saves it to the database.

        Parameters:
        -----------
        start_date : str
            The start date for the data import in the format "YYYY-MM-DD".
        end_date : str
            The end date for the data import in the format "YYYY-MM-DD".
        """
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

    def import_data(self, start_date: str, end_date: str) -> None:
        # Set up logging
        
        year_range  = self._get_year_range(start_date,end_date)

        for start_date, end_date in year_range:

            my_request = requests.get(self._create_endpoint(start_date, end_date))

            logging.info(f"REQUETE: {start_date},{len((my_request.json()['records']))}")

            self._insert(my_request)

    def _insert(self, my_request: requests.Response) -> None:
        """
        Private method that inserts data into the database from a given requests.Response object.

        Args:
            my_request (requests.Response): The Response object containing the data to be inserted.

        Returns:
            None.
        """
        # df = pd.DataFrame(columns=['date', 'Temperature'])
        row_record =[]
        for row in my_request.json()["records"]:
            row_data = {} 
            for field in self.field_list:
                try: 
                    row_data[field[0]] = row["fields"][field[1]]
                except KeyError:
                    row_data[field[0]] = None
            row_record.append(row_data)        
            # df = df.append(row_data, ignore_index=True)
        df = pd.DataFrame.from_records(row_record)

        df = self.agregate_temp_by_day(df)
        for row in df.to_dict(orient='records'):
            logging.debug(row)
            self.session.add(self.TableModel(**row))
        
        self.session.commit()

    def agregate_temp_by_day(self,df):
        df.index = pd.to_datetime(df.date,utc=True)
        df = df.drop(columns=["date"])

        # Group by departement and day
        df_temp = df.resample('D').agg("mean")

        df_temp = df_temp.reset_index()
        df_temp["date"] = pd.to_datetime(df_temp["date"]).dt.strftime('%Y-%m-%d')
        # df_temp["date"] = pd.to_datetime(df_temp["date"]).dt.date
        return df_temp



class GareImporter(Importer):

    station_list = ["Paris Austerlitz", "Paris Est", "Paris Gare de Lyon", "Paris Gare du Nord", "Paris Montparnasse", "Paris Saint-Lazare", "Paris Bercy"]

    def _init_attributes(self):
        self.TableModel= Gare
        self.field_list = [
            ["latitude", "latitude_entreeprincipale_wgs84"],
            ["longitude", "longitude_entreeprincipale_wgs84"],
        ]

    def _create_endpoint(self,station:str)->Tuple[str,str]:
        URL_geo = "https://ressources.data.sncf.com/api/records/1.0/search/"
        ressource_geo = "?dataset=referentiel-gares-voyageurs"
        row_limit_geo ="&rows=1"
        stationt_geo = f"&refine.gare_alias_libelle_noncontraint={station}"
        endpoint_gare = URL_geo + ressource_geo + row_limit_geo + stationt_geo
         
    
        URL_freq = "https://ressources.data.sncf.com/api/records/1.0/search/"
        ressource_freq = "?dataset=frequentation-gares"
        row_limit_freq ="&rows=1"
        station_freq = f"&refine.nom_gare={station}"
        endpoint_freq =  URL_freq + ressource_freq + row_limit_freq + station_freq
        
        return (endpoint_gare,endpoint_freq)


    def import_data(self):
        
        for station in self.station_list:
            if station == "Paris Bercy":
                station_lib = "Paris Bercy Bourgogne - Pays d'Auvergne"
                
            else:
                station_lib = station

            my_request_geo = requests.get(self._create_endpoint(station_lib)[0])
            my_request_freq = requests.get(self._create_endpoint(station_lib)[1])
            
            logging.info(f"REQUETE: {station}")
            
            self._insert(my_request_geo, my_request_freq, station)

    def _insert(self, my_request_geo: requests.Response, my_request_freq: requests.Response, station:str) -> None:

        geo_data = my_request_geo.json()["records"][0] # Only one row is collected for each station       
        row_data = {} 
        for field in self.field_list:
            try: 
                row_data[field[0]] = geo_data["fields"][field[1]]
            except KeyError:
                row_data[field[0]] = None

        freq_data = my_request_freq.json()["records"][0]
        row_data["freq_2019"] = freq_data["fields"]["total_voyageurs_non_voyageurs_2019"]+freq_data["fields"]["total_voyageurs_2019"]
        row_data["freq_2020"] = freq_data["fields"]["total_voyageurs_non_voyageurs_2020"]+freq_data["fields"]["total_voyageurs_2020"]
        row_data["freq_2021"] = freq_data["fields"]["total_voyageurs_non_voyageurs_2021"]+freq_data["fields"]["total_voyageurs_2021"]

        # self.session.add(LostItem(**temp_data))
        self.session.add(Gare(nom_gare=station,**row_data))
        self.session.commit()


if __name__ == "__main__":
    engine = create_engine('sqlite:///db.sqlite')
    my_import = LostItemImporter(engine)
    my_import.clean()
    # my_import.import_by_date("01 january 2018", "now")