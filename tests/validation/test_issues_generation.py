import json
import os
import unittest
import requests

from mock import patch

from excel.validate import validate_dict_from_excel
from validation.validation_service import ValidationService


class TestIssuesGeneration(unittest.TestCase):

    def setUp(self):
        self.validation_service = ValidationService("")

    @patch('validation.validation_service.requests.post')
    def test_when_validate_invalid_entity_with_valid_schema_should_return_errors(self, mock_post):
        mock_post.return_value.json.side_effect = ([
                {
                    'dataPath': '.assembly_type',
                    'errors': [
                        'should be equal to one of the allowed values: ["covid-19 outbreak"]'
                    ]
                },
                {
                    'dataPath': '.coverage',
                    'errors': [
                        "should have required property 'coverage'"
                    ]
                }
            ],
            [
                {
                    "dataPath": ".email_address",
                    "errors": [
                        "should have required property 'email_address'"
                    ]
                }
            ],
            [],
            []
        )
        mock_post.return_value.status = requests.codes.ok

        current_folder = os.path.dirname(__file__)
        with open(os.path.join(current_folder, "../resources/data_for_test_issues.json")) as test_data_file:
            test_data = json.load(test_data_file)
        with open(os.path.join(current_folder, "../resources/test_issues.json")) as test_issues_file:
            expected_test_issues = json.load(test_issues_file)

        actual_issues = self.validation_service.validate_data(test_data)

        self.assertEqual(expected_test_issues, actual_issues)
