import json
import os

import requests
import unittest

from mock import Mock, patch

from validation.not_known_entity_exception import NotKnownEntityException
from validation.validation_service import ValidationService
from validation.validation_state import ValidationState


class TestValidationService(unittest.TestCase):

    def setUp(self):
        self.validation_service = ValidationService("")

    @patch('validation.validation_service.requests.post')
    def test_when_validate_valid_entity_with_valid_schema_should_return_no_errors(self, mock_post):
        mock_post.return_value.json.return_value = []
        mock_post.return_value.status = requests.codes.ok

        schema = {}
        object_to_validate = {}

        validation_response = self.validation_service.validate_by_schema(schema, object_to_validate)
        validation_errors = validation_response.json()

        self.assertEqual(0, len(validation_errors))

    @patch('validation.validation_service.requests.post')
    def test_when_validate_invalid_entity_with_valid_schema_should_return_errors(self, mock_post):
        mock_post.return_value.json.return_value = [
            {
                "dataPath": ".release_date",
                "errors": [
                    "should have required property 'release_date'"
                ]
            }
        ]
        mock_post.return_value.status = requests.codes.ok

        schema = {}
        object_to_validate = {}

        validation_response = self.validation_service.validate_by_schema(schema, object_to_validate)
        validation_errors = validation_response.json()

        self.assertEqual(len(validation_errors), 1)

    def test_when_passing_valid_entity_type_returns_schema_name(self):
        entity_type = "study"
        expected_schema_name = "study_schema"

        self.assertEqual(expected_schema_name, self.validation_service.get_schema_by_entity_type(entity_type))

    def test_when_passing_invalid_entity_type_returns_error_message(self):
        entity_type = "not_valid_entity_name"

        with self.assertRaises(NotKnownEntityException) as context:
            self.validation_service.get_schema_by_entity_type(entity_type)

        self.assertEqual(NotKnownEntityException, context.exception.__class__)
        self.assertEqual(entity_type, context.exception.entity_name)
        self.assertTrue(context.exception.__str__().__contains__(entity_type))

    @patch('validation.validation_service.requests.post')
    def test_when_all_entities_valid_returns_empty_error_result(self, mock_post):
        mock_post.return_value.json.return_value = []
        mock_post.return_value.status = requests.codes.ok

        current_folder = os.path.dirname(__file__)
        with open(os.path.join(current_folder, "../resources/valid_spreadsheet.json")) as valid_spreadsheet_file:
            valid_json_from_spreadsheet = json.load(valid_spreadsheet_file)

        validation_result = self.validation_service.validate_spreadsheet_json(valid_json_from_spreadsheet)

        self.assertEqual(0, len(validation_result['errors']))
        self.assertEqual(ValidationState.PASS, validation_result['state'])

    @patch('validation.validation_service.requests.post')
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
        mock_post.return_value.status = requests.codes.ok

        current_folder = os.path.dirname(__file__)
        with open(os.path.join(current_folder, "../resources/invalid_spreadsheet.json")) as valid_spreadsheet_file:
            valid_json_from_spreadsheet = json.load(valid_spreadsheet_file)

        validation_result = self.validation_service.validate_spreadsheet_json(valid_json_from_spreadsheet)

        self.assertEqual(1, len(validation_result['errors'][0]))
        self.assertEqual(ValidationState.FAIL, validation_result['state'])


if __name__ == '__main__':
    unittest.main()
