from db.model import LostItem, create_tables
from db.import_classes import LostItemImporter, TemperatureImporter, GareImporter
from sqlalchemy import create_engine

engine = create_engine('sqlite:///db.sqlite')
gare = GareImporter(engine)
gare.clean()
gare.import_data()
# temperature = TemperatureImporter(engine)
# temperature.update()
# temperature.clean()
# temperature.import_data("01 january 2018", "now")
# lostitem = LostItemImporter(engine)
# lostitem.clean()
# lostitem.import_data("01 january 2018", "now")
# print(my_import._get_last_date())
# my_import.update()