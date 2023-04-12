from db.model import LostItem, create_tables
from db.import_classes import LostItemImporter, TemperatureImporter, GareImporter, Importer
from sqlalchemy import create_engine
import pandas as pd



engine = create_engine('sqlite:///db.sqlite')



# gare_importer = GareImporter(engine)
# gare_importer.import_data()



temperature = TemperatureImporter(engine)
temperature.clean()
temperature.import_data("01 january 2018","now")
# temperature.update()

# lostitem = LostItemImporter(engine)
# # lostitem.clean()
# lostitem.import_data("01 january 2018", "now")
# # lostitem.update()