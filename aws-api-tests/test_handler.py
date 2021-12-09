from pprint import pprint
import unittest
import boto3
import datetime

from botocore.exceptions import ClientError
from moto import mock_dynamodb2
from utils.pydantic_datamodel import convert_string_to_dt_object


@mock_dynamodb2
class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        """
        Create database resource and mock table
        """
        from create_mock_event_table import create_event_table
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        self.table = create_event_table(self.dynamodb)

    def tearDown(self):
        """
        Delete database resource and mock table
        """
        self.table.delete()
        self.dynamodb = None

    def test_table_exists(self):
        """
        Test if our mock table is ready
        """
        def test_table_exists(self):
            self.assertIn('events', self.table.name)

    def test_put_event(self):
        from put_mock_event import put_event
        result = put_event(1, "Generic Test Event", "completed",
                           convert_string_to_dt_object("2021-12-06 17:27:04").isoformat(),
                           convert_string_to_dt_object("2021-12-06 18:27:04").isoformat(),
                           self.dynamodb)
        self.assertEqual(200, result['ResponseMetadata']['HTTPStatusCode'])


if __name__ == '__main__':
    unittest.main()
