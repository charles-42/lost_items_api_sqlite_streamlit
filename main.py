from db.model import create_tables
from db.import_classes import LostItemImporter, TemperatureImporter, GareImporter
from sqlalchemy import create_engine



engine = create_engine('sqlite:///db.sqlite')

gare_importer = GareImporter(engine)
gare_importer.import_data()

temperature_importer = TemperatureImporter(engine)
temperature_importer.import_data("01-01-2022","now")

lostitem_importer = LostItemImporter(engine)
lostitem_importer.import_data("01-01-2022","now")