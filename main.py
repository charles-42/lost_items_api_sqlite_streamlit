from db.model import LostItem, create_tables
from db.import_classes import LostItemImporter
from sqlalchemy import create_engine

engine = create_engine('sqlite:///db.sqlite')
my_import = LostItemImporter(engine)
my_import.clean()
my_import.import_by_date("01 january 2018", "now")