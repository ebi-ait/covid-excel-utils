import json
import unittest
import requests

from os.path import dirname, join
from mock import patch

from validation.schema import SchemaValidator
from submission.submission import Submission


class TestSchemaValidation(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        with open(join(dirname(__file__), "../../resources/data_for_test_issues.json")) as test_data_file:
            test_data = json.load(test_data_file)
        self.schema_validation = SchemaValidator("")
        self.submission = Submission()
        for entity_type, attributes in test_data.items():
            self.submission.map(entity_type, attributes["index"], attributes.get("accession", ""), attributes)

    @patch('validation.schema.requests.post')
    def test_when_entity_valid_should_return_no_errors(self, mock_post):
        # Given
        mock_post.return_value.json.return_value = []
        mock_post.return_value.status = requests.codes['ok']

        # When
        self.schema_validation.validate_data(self.submission)

        # Then
        self.assertFalse(self.submission.has_errors())
        self.assertDictEqual({}, self.submission.get_all_errors())

    @patch('validation.schema.requests.post')
    def test_when_entity_invalid_entity_with_valid_schema_should_return_errors(self, mock_post):
        # Given
        mock_post.return_value.json.return_value = [
            {
                "dataPath": ".release_date",
                "errors": [
                    "should have required property 'release_date'"
                ]
            }
        ]
        mock_post.return_value.status = requests.codes['ok']
        expected_errors = {
            "isolate_genome_assembly_information": {
                "P17157_1007": {
                    "release_date": ["should have required property 'release_date'"]
                }
            },
            "study": {
                "PRJEB39632": {
                    "release_date": ["should have required property 'release_date'"]
                }
            },
            "sample": {
                "ERS4858671": {
                    "release_date": ["should have required property 'release_date'"]
                }
            },
            "run_experiment": {
                "ERX4331406": {
                    "release_date": ["should have required property 'release_date'"]
                }
            }
        }
        study = self.submission.get_entity('study', 'PRJEB39632')
        # When
        self.schema_validation.validate_data(self.submission)

        # Then
        self.assertTrue(study.errors)
        self.assertTrue(self.submission.has_errors())
        self.assertDictEqual(expected_errors['study']['PRJEB39632'], study.errors)
        self.assertDictEqual(expected_errors['study'], self.submission.get_type_errors('study'))
        self.assertDictEqual(expected_errors, self.submission.get_all_errors())


if __name__ == '__main__':
    unittest.main()
