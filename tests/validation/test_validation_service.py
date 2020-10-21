import requests
import unittest

from mock import Mock, patch

from validation.validation_service import ValidationService


class TestValidationService(unittest.TestCase):

    def setUp(self):
        self.validation_service = ValidationService("")

    @patch('validation.validation_service.requests.post')
    def test_when_validate_valid_entity_with_valid_schema_should_return_no_errors(self, mock_post):
        mock_post.return_value.json.return_value = []
        mock_post.return_value.status = requests.codes.ok

        schema = {}
        object_to_validate = {}

        validation_response = self.validation_service.validate(schema, object_to_validate)
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

        validation_response = self.validation_service.validate(schema, object_to_validate)
        validation_errors = validation_response.json()

        self.assertEqual(len(validation_errors), 1)


if __name__ == '__main__':
    unittest.main()
