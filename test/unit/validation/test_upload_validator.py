from submission.entity import Entity
from test.unit import validation
import unittest
from unittest.mock import patch, MagicMock

from validation.upload import UploadValidator, CHECKSUMS_FILE_NAME

class TestUploadValidator(unittest.TestCase):
    @patch.object(UploadValidator, 'get_checksums_file')
    def test_get_checksums_file_should_be_called_with_params(self, mock: MagicMock):
        # Given
        secure_key = 'uuid'
        file_name = 'file_name.extension1.ex2'
        checksum = 'checksum'
        mock.return_value = f"{file_name},{checksum}"
        expected_checksums_file = {
            file_name: checksum
        }

        # When
        validator = UploadValidator(secure_key)
        
        # Then
        mock.assert_called_once_with(f'{secure_key}/{CHECKSUMS_FILE_NAME}')
        self.assertDictEqual(expected_checksums_file, validator.file_checksum_map)
    
    @patch.object(UploadValidator, 'get_checksums_file')
    def test_missing_file_should_log_error(self, mock: MagicMock):
        # Given
        entity_type = 'run_experiment'
        index = f'{entity_type}1'
        mock.return_value = f"file_name.extension1.ex2,checksum"
        validator = UploadValidator('uuid')
        entity = Entity(entity_type, index, {'uploaded_file_1': 'missing.file'})
        expected_errors = {
            'uploaded_file_1': ['File has not been uploaded to drag-and-drop: missing.file']
        }
        # When
        validator.validate_entity(entity)

        # Then
        self.assertDictEqual(expected_errors, entity.get_errors())
    
    @patch.object(UploadValidator, 'get_checksums_file')
    def test_missmatched_checksum_should_log_error(self, mock: MagicMock):
        # Given
        secure_key = 'uuid'
        entity_type = 'run_experiment'
        index = f'{entity_type}1'
        file_name = 'file_name.extension1.ex2'
        expected_checksum = 'checksum'
        wrong_checksum = 'not-checksum'
        mock.return_value = f"{file_name},{expected_checksum}"

        # When
        validator = UploadValidator(secure_key)
        attributes = {
            'uploaded_file_1': file_name,
            'uploaded_file_1_checksum': wrong_checksum
        }
        entity = Entity(entity_type, index, attributes)
        validator.validate_entity(entity)

        # Then
        expected_errors = {
            'uploaded_file_1_checksum': [f'The checksum found on drag-and-drop {expected_checksum} does not match: {wrong_checksum}']
        }
        self.assertDictEqual(expected_errors, entity.get_errors())

    @patch.object(UploadValidator, 'get_checksums_file')
    def test_validation_should_edit_file_attributes(self, mock: MagicMock):
        # Given
        secure_key = 'uuid'
        entity_type = 'run_experiment'
        index = f'{entity_type}1'
        file_name = 'file_name.extension1.ex2'
        checksum = 'checksum'
        mock.return_value = f"{file_name},{checksum}"

        # When
        validator = UploadValidator(secure_key)
        attributes = {
            'uploaded_file_1': file_name
        }
        entity = Entity(entity_type, index, attributes)
        validator.validate_entity(entity)

        # Then
        expected_attributes = {
            'uploaded_file_1': file_name,
            'uploaded_file_1_checksum': checksum,
        }
        self.assertDictEqual(expected_attributes, entity.attributes)

    @patch.object(UploadValidator, 'get_checksums_file')
    def test_validation_with_second_file_missing(self, mock: MagicMock):
        # Given
        secure_key = 'uuid'
        entity_type = 'run_experiment'
        index = f'{entity_type}1'
        mock.return_value = f"first-file,first-checksum"
        
        # When
        validator = UploadValidator(secure_key)
        attributes = {
            'uploaded_file_1': 'first-file',
            'uploaded_file_2': 'second-file'
        }
        entity = Entity(entity_type, index, attributes)
        validator.validate_entity(entity)

        # Then
        expected_errors = {
            'uploaded_file_2': ['File has not been uploaded to drag-and-drop: second-file']
        }
        self.assertDictEqual(expected_errors, entity.get_errors())

    @patch.object(UploadValidator, 'get_checksums_file')
    def test_validation_with_second_file_present(self, mock: MagicMock):
        # Given
        secure_key = 'uuid'
        entity_type = 'run_experiment'
        index = f'{entity_type}1'
        mock.return_value = f"first-file,first-checksum\n" \
                            f"second-file,second-checksum"
        # When
        validator = UploadValidator(secure_key)
        attributes = {
            'uploaded_file_1': 'first-file',
            'uploaded_file_1_checksum': 'first-checksum',
            'uploaded_file_2': 'second-file',
            'uploaded_file_2_checksum': 'second-checksum',
        }
        entity = Entity(entity_type, index, attributes)
        validator.validate_entity(entity)

        # Then
        self.assertDictEqual({}, entity.get_errors())
