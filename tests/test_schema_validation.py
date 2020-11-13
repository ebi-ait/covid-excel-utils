import json
import unittest
import requests
from os.path import dirname, join
from mock import patch
from validation.schema import SchemaValidation


class TestSchemaValidation(unittest.TestCase):

    def setUp(self):
        self.schema_validation = SchemaValidation("")

    @patch('validation.schema.requests.post')
    def test_when_validate_valid_entity_with_valid_schema_should_return_no_errors(self, mock_post):
        mock_post.return_value.json.return_value = []
        mock_post.return_value.status = requests.codes['ok']

        entity_type = ''
        entity = {}

        validation_errors = self.schema_validation.validate_entity(entity_type, entity)

        self.assertEqual(0, len(validation_errors))

    @patch('validation.schema.requests.post')
    def test_when_validate_invalid_entity_with_valid_schema_should_return_errors(self, mock_post):
        mock_post.return_value.json.return_value = [
            {
                "dataPath": ".release_date",
                "errors": [
                    "should have required property 'release_date'"
                ]
            }
        ]
        mock_post.return_value.status = requests.codes['ok']

        entity_type = ''
        entity = {}

        validation_errors = self.schema_validation.validate_entity(entity_type, entity)

        self.assertEqual(len(validation_errors), 1)

    @patch('validation.schema.requests.post')
    def test_when_all_entities_valid_returns_empty_error_result(self, mock_post):
        mock_post.return_value.json.return_value = []
        mock_post.return_value.status = requests.codes['ok']

        with open(join(dirname(__file__), "resources/valid_spreadsheet.json")) as valid_file:
            valid_json = json.load(valid_file)

        validation_result = self.schema_validation.validate_data(valid_json)

        self.assertEqual(0, len(validation_result))

    @patch('validation.schema.requests.post')
    def test_when_some_entities_invalid_returns_error_result(self, mock_post):
        mock_post.return_value.json.side_effect = ([
                {
                    "dataPath": ".release_date",
                    "errors": [
                        "should have required property 'release_date'"
                    ]
                }
            ],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            []
        )
        mock_post.return_value.status = requests.codes['ok']

        with open(join(dirname(__file__), "resources/invalid_spreadsheet.json")) as invalid_file:
            invalid_json = json.load(invalid_file)

        validation_result = self.schema_validation.validate_data(invalid_json)
        self.assertEqual(1, len(validation_result))


if __name__ == '__main__':
    unittest.main()
