import unittest
from datetime import datetime
from db.import_lost_items import parse_date, get_year_range, request_by_year_and_station, import_lost_item

class TestParseDate(unittest.TestCase):

    def test_parse_date_YYYY_MM_DD(self):
        start_date = "2022-01-01"
        end_date = "2022-01-31"
        start_parse, end_parse = parse_date(start_date, end_date)

        # Check that start_parse and end_parse are datetime objects
        self.assertIsInstance(start_parse, datetime)
        self.assertIsInstance(end_parse, datetime)

        # Check that the parsed dates match the expected dates
        self.assertEqual(start_parse.date(), datetime(2022, 1, 1).date())
        self.assertEqual(end_parse.date(), datetime(2022, 1, 31).date())

    def test_parse_date_letters(self):
        start_date = "1 january 2022"
        end_date = "31 december 2022"
        start_parse, end_parse = parse_date(start_date, end_date)

        # Check that start_parse and end_parse are datetime objects
        self.assertIsInstance(start_parse, datetime)
        self.assertIsInstance(end_parse, datetime)

        # Check that the parsed dates match the expected dates
        self.assertEqual(start_parse.date(), datetime(2022, 1, 1).date())
        self.assertEqual(end_parse.date(), datetime(2022, 12, 31).date())

    def test_parse_date_now(self):
        start_date = "2022-01-01"
        end_date = "now"
        start_parse, end_parse = parse_date(start_date, end_date)

        # Check that start_parse and end_parse are datetime objects
        self.assertIsInstance(start_parse, datetime)
        self.assertIsInstance(end_parse, datetime)

        # Check that the parsed dates match the expected dates
        self.assertEqual(start_parse.date(), datetime(2022, 1, 1).date())
        self.assertEqual(end_parse.date(), datetime.now().date())

class TestGetYearRange(unittest.TestCase):

    def test_get_year_range(self):
        start_date = "2022-06-15"
        end_date = "2024-03-20"
        year_ranges = get_year_range(start_date, end_date)

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

class TestRequestByYearAndStation(unittest.TestCase):
    def test_request_by_year_and_station(self):
        station = "Paris Est"
        start = "2022-01-01"
        end = "2022-12-31"
        expected_endpoint = "https://ressources.data.sncf.com/api/records/1.0/search/?dataset=objets-trouves-restitution&q=date%3A%5B2022-01-01+TO+2022-12-31%5D&rows=10000&refine.gc_obo_gare_origine_r_name=Paris+Est"

        # Call the function and check the result
        result = request_by_year_and_station(station, start, end)
        self.assertEqual(result, expected_endpoint)

import unittest
from unittest.mock import patch, MagicMock
from datetime import date
from db.model import LostItem

class TestImportLostItem(unittest.TestCase):

    @patch('requests.get')
    @patch('sqlalchemy.orm.sessionmaker')
    @patch('sqlalchemy.create_engine')

    def test_import_lost_item(self, mock_create_engine, mock_sessionmaker, mock_requests_get):
        
        mock_session = MagicMock()
        mock_sessionmaker.return_value = MagicMock(return_value=mock_session)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "records": [
                {
                    "fields": {
                        "date": "2022-04-01",
                        "gc_obo_type_c": "Laptop",
                        "gc_obo_gare_origine_r_name": "Paris Gare de Lyon",
                        "gc_obo_date_heure_restitution_c": None
                    }
                },
                {
                    "fields": {
                        "date": "2022-03-15",
                        "gc_obo_type_c": "Phone",
                        "gc_obo_gare_origine_r_name": "Paris Est",
                        "gc_obo_date_heure_restitution_c": "2022-03-20T14:00:00+01:00"
                    }
                }
            ]
        }
        mock_requests_get.return_value = mock_response

        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        start_date = "1 march 2022"
        end_date = "30 april 2022"

        import_lost_item(start_date, end_date)

        mock_create_engine.assert_called_once_with('sqlite:///db.sqlite')
        mock_sessionmaker.assert_called_once_with(bind=mock_engine)
        mock_session.query.assert_called_once_with(LostItem)
        mock_session.query.return_value.delete.assert_called_once()
        mock_session.commit.assert_called()

        expected_calls = [
            ((mock_response.json()['records'][0]['fields']),),
            ((mock_response.json()['records'][1]['fields']),)
        ]

        for truc in mock_session.add.call_args_list:
            print(truc.args[0].date)
        print(expected_calls)


        self.assertEqual(mock_session.add.call_args_list, expected_calls)
        
        mock_session.commit.assert_called()



if __name__ == '__main__':
    unittest.main()