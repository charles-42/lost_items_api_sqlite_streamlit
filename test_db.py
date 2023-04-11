

import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.model import LostItem, create_tables
from db.import_classes import LostItemImporter
from datetime import datetime


class TestLostItemImporter(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        create_tables(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.importer = LostItemImporter(self.engine)
        

    # def tearDown(self):
    #     self.session.close()
    #     self.engine.dispose()


    def test__parse_date_YYYY_MM_DD(self):
        start_date = "2022-01-01"
        end_date = "2022-01-31"
        start_parse, end_parse = self.importer._parse_date(start_date, end_date)

        # Check that start_parse and end_parse are datetime objects
        self.assertIsInstance(start_parse, datetime)
        self.assertIsInstance(end_parse, datetime)

        # Check that the parsed dates match the expected dates
        self.assertEqual(start_parse.date(), datetime(2022, 1, 1).date())
        self.assertEqual(end_parse.date(), datetime(2022, 1, 31).date())

    def test__parse_date_letters(self):
        start_date = "1 january 2022"
        end_date = "31 december 2022"
        start_parse, end_parse = self.importer._parse_date(start_date, end_date)

        # Check that start_parse and end_parse are datetime objects
        self.assertIsInstance(start_parse, datetime)
        self.assertIsInstance(end_parse, datetime)

        # Check that the parsed dates match the expected dates
        self.assertEqual(start_parse.date(), datetime(2022, 1, 1).date())
        self.assertEqual(end_parse.date(), datetime(2022, 12, 31).date())

    def test__parse_date_now(self):
        start_date = "2022-01-01"
        end_date = "now"
        start_parse, end_parse = self.importer._parse_date(start_date, end_date)

        # Check that start_parse and end_parse are datetime objects
        self.assertIsInstance(start_parse, datetime)
        self.assertIsInstance(end_parse, datetime)

        # Check that the parsed dates match the expected dates
        self.assertEqual(start_parse.date(), datetime(2022, 1, 1).date())
        self.assertEqual(end_parse.date(), datetime.now().date())

    def test__get_year_range(self):

        start_date = "2022-06-15"
        end_date = "2024-03-20"
        year_ranges = self.importer._get_year_range(start_date, end_date)

        # Check that year_ranges is a list and has the correct length
        self.assertIsInstance(year_ranges, list)
        self.assertEqual(len(year_ranges), 3)

        # Check that each year range tuple has the expected format
        for year_range in year_ranges:
            self.assertIsInstance(year_range, tuple)
            self.assertEqual(len(year_range), 2)
            self.assertIsInstance(year_range[0], str)
            self.assertIsInstance(year_range[1], str)
            self.assertRegex(year_range[0], r"\d{4}-\d{2}-\d{2}")
            self.assertRegex(year_range[1], r"\d{4}-\d{2}-\d{2}")

        # Check that the first and last year ranges match the expected dates
        self.assertEqual(year_ranges[0], ("2022-06-15", "2022-12-31"))
        self.assertEqual(year_ranges[1], ("2023-01-01", "2023-12-31"))
        self.assertEqual(year_ranges[-1], ("2024-01-01", "2024-03-20"))

    def test__create_endpoint(self):
        station = "Paris Est"
        start = "2022-01-01"
        end = "2022-12-31"
        expected_endpoint = "https://ressources.data.sncf.com/api/records/1.0/search/?dataset=objets-trouves-restitution&q=date%3A%5B2022-01-01+TO+2022-12-31%5D&rows=10000&refine.gc_obo_gare_origine_r_name=Paris+Est"

        # Call the function and check the result
        result = self.importer._create_endpoint(station, start, end)
        self.assertEqual(result, expected_endpoint)

    def test__insert(self):
        data = {'records': [{'fields': {'date': '2022-01-01', 'gc_obo_type_c': 'SAC', 'gc_obo_gare_origine_r_name': 'Paris Austerlitz', 'gc_obo_date_heure_restitution_c': None}}]}
        my_request = MagicMock()
        my_request.json.return_value = data
        self.importer._insert(my_request)
        self.assertEqual(self.session.query(LostItem).count(), 1)