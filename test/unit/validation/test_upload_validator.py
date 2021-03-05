from submission.entity import Entity
from test.unit import validation
import unittest
from unittest.mock import patch, MagicMock

from submission.submission import Submission
from validation.upload import UploadValidator

class TestUploadValidator(unittest.TestCase):
    @patch.object(UploadValidator, 'get_file_keys')
    def test_file_manifest_should_remove_xlsx(self, mock: MagicMock):
        # Given
        secure_key = 'uuid'
        file_name = 'file_name.extention1.ex2'
        checksum = 'checksum'
        mock.return_value = {
            f'{secure_key}/{file_name}.{checksum}',
            f'{secure_key}/meta_file.XLSX.date-time-stamp'
        }
        expected_manifest = {
            file_name: checksum
        }

        # When
        validator = UploadValidator(secure_key)
        
        # Then
        mock.assert_called_once_with(f'{secure_key}/')
        self.assertDictEqual(expected_manifest, validator.file_manifest)
    
    @patch.object(UploadValidator, 'get_file_keys')
    def test_missing_file_should_log_error(self, mock: MagicMock):
        # Given
        secure_key = 'uuid'
        entity_type = 'run_experiment'
        index = f'{entity_type}1'

        mock.return_value = {
            f'{secure_key}/file_name.extention1.ex2.checksum',
            f'{secure_key}/meta_file.XLSX.date-time-stamp'
        }
        validator = UploadValidator(secure_key)
        entity = Entity(entity_type, index, {'uploaded_file_1': 'missing.file'})
        expected_errors = {
            'uploaded_file_1': ['File has not been uploaded to drag-and-drop: missing.file']
        }
        # When
        validator.validate_entity(entity)

        # Then
        self.assertDictEqual(expected_errors, entity.errors)
    
    @patch.object(UploadValidator, 'get_file_keys')
    def test_missmatched_checksum_should_log_error(self, mock: MagicMock):
        # Given
        secure_key = 'uuid'
        entity_type = 'run_experiment'
        index = f'{entity_type}1'
        file_name = 'file_name.extention1.ex2'
        expected_checksum = 'checksum'
        wrong_checksum = 'not-checksum'
        mock.return_value = {
            f'{secure_key}/{file_name}.{expected_checksum}',
            f'{secure_key}/meta_file.XLSX.date-time-stamp'
        }
        
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
        self.assertDictEqual(expected_errors, entity.errors)

    @patch.object(UploadValidator, 'get_file_keys')
    def test_validation_should_add_checksum_to_attributes(self, mock: MagicMock):
        # Given
        secure_key = 'uuid'
        entity_type = 'run_experiment'
        index = f'{entity_type}1'
        file_name = 'file_name.extention1.ex2'
        checksum = 'checksum'
        mock.return_value = {
            f'{secure_key}/{file_name}.{checksum}',
            f'{secure_key}/meta_file.XLSX.date-time-stamp'
        }
        
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

    @patch.object(UploadValidator, 'get_file_keys')
    def test_validation_with_second_file_missing(self, mock: MagicMock):
        # Given
        secure_key = 'uuid'
        entity_type = 'run_experiment'
        index = f'{entity_type}1'
        mock.return_value = {
            f'{secure_key}/first-file.first-checksum',
            f'{secure_key}/meta_file.XLSX.date-time-stamp'
        }
        
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
        self.assertDictEqual(expected_errors, entity.errors)


    @patch.object(UploadValidator, 'get_file_keys')
    def test_validation_with_second_file_present(self, mock: MagicMock):
        # Given
        secure_key = 'uuid'
        entity_type = 'run_experiment'
        index = f'{entity_type}1'
        mock.return_value = {
            f'{secure_key}/first-file.first-checksum',
            f'{secure_key}/second-file.second-checksum',
            f'{secure_key}/meta_file.XLSX.date-time-stamp'
        }
        
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
        self.assertDictEqual({}, entity.errors)