import json
import os
import unittest
import requests
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

        validation_errors = self.schema_validation.validate(entity_type, entity)

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

        validation_errors = self.schema_validation.validate(entity_type, entity)

        self.assertEqual(len(validation_errors), 1)

    @patch('validation.schema.requests.post')
    def test_when_all_entities_valid_returns_empty_error_result(self, mock_post):
        mock_post.return_value.json.return_value = []
        mock_post.return_value.status = requests.codes['ok']

        current_folder = os.path.dirname(__file__)
        with open(os.path.join(current_folder, "resources/valid_spreadsheet.json")) as valid_spreadsheet_file:
            valid_json_from_spreadsheet = json.load(valid_spreadsheet_file)

        validation_result = self.schema_validation.validate_data(valid_json_from_spreadsheet)

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

        current_folder = os.path.dirname(__file__)
        with open(os.path.join(current_folder, "resources/invalid_spreadsheet.json")) as valid_spreadsheet_file:
            valid_json_from_spreadsheet = json.load(valid_spreadsheet_file)

        validation_result = self.schema_validation.validate_data(valid_json_from_spreadsheet)

        self.assertEqual(1, len(validation_result))


if __name__ == '__main__':
    unittest.main()
