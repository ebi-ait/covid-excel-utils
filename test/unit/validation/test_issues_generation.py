import json
import unittest
from os.path import dirname, join

import requests
from unittest.mock import patch

from validation.json import JsonValidator
from submission.submission import Submission


class TestIssuesGeneration(unittest.TestCase):
    def setUp(self):
        self.schema_validation = JsonValidator("")
        self.maxDiff = None
        current_folder = dirname(__file__)
        with open(join(current_folder, "../../resources/data_for_test_issues.json")) as test_data_file:
            test_data = json.load(test_data_file)
        self.submission = Submission()
        for entity_type, attributes in test_data.items():
            self.submission.map(entity_type, attributes["index"], attributes)

    @patch('validation.json.requests.post')
    def test_when_validate_invalid_entity_with_valid_schema_should_return_errors(self, mock_post):
        # Given
        mock_post.return_value.json.side_effect = ([
                {
                    'dataPath': '.assembly_type',
                    'errors': [
                        'should be equal to one of the allowed values: [\'covid-19 outbreak\']'
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
        mock_post.return_value.status = requests.codes['ok']
        expected_issues = {
            "isolate_genome_assembly_information": {
                "P17157_1007": {
                    "assembly_type": ["should be equal to one of the allowed values: ['covid-19 outbreak']"],
                    "coverage": ["should have required property 'coverage'"]
                }
            },
            "study": {
                "PRJEB39632": {
                    "email_address": ["should have required property 'email_address'"]
                }
            }
        }
        
        # When
        self.schema_validation.validate_data(self.submission)
        
        # Then
        self.assertDictEqual(expected_issues, self.submission.get_all_errors())


if __name__ == '__main__':
    unittest.main()
