from db.model import create_tables
from db.import_classes import LostItemImporter, TemperatureImporter, GareImporter
from sqlalchemy import create_engine



engine = create_engine('sqlite:///db.sqlite')

# gare_importer = GareImporter(engine)
# gare_importer.import_data()

temperature_importer = TemperatureImporter(engine)
# temperature_importer.clean()
# temperature_importer.import_data("01-01-2018","now")
temperature_importer.update()

# lostitem_importer = LostItemImporter(engine)
# lostitem_importer.update()
# lostitem_importer.clean()
# lostitem_importer.import_data("01-01-2018","now")