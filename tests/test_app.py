# add files to python path
import sys
import os
import inspect    
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

import unittest
import pandas as pd
import plotly.express as px
from db.import_classes import LostItemImporter, TemperatureImporter
from sqlalchemy import create_engine

# Import the functions to be tested
from utils import get_importers, histogramme


class TestFunctions(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        self.temperature_importer = TemperatureImporter(self.engine)
        self.lostitem_importer = LostItemImporter(self.engine)
        self.df = pd.DataFrame({
            'type_objet': ['phone', 'wallet', 'phone'],
            'date': ['2022-01-01', '2022-01-02', '2022-01-02']
        })

    def test_get_importers(self):
        # Test that the function returns TemperatureImporter and LostItemImporter objects
        temperature_importer, lostitem_importer = get_importers()
        self.assertIsInstance(temperature_importer, TemperatureImporter)
        self.assertIsInstance(lostitem_importer, LostItemImporter)


    def test_histogramme(self):
        # Test that the function returns a plotly histogram object
        fig = histogramme(self.df)

        # Test that the histogram object has the correct layout and traces
        self.assertEqual(fig.layout.width, 1000)
        self.assertEqual(fig.layout.bargap, 0.1)
        self.assertEqual(fig.layout.xaxis.title.text, "Date où l'objet a été trouvé")
        self.assertEqual(fig.layout.yaxis.title.text, "Nombre d'objets trouvés par semaine")
        self.assertEqual(len(fig.data), 2)
        self.assertEqual(fig.data[0].x[0], '2022-01-01')
        self.assertEqual(fig.data[1].x[0], '2022-01-02')