import logging
from typing import List

from validation.base import BaseValidator
from .load import ExcelLoader


class ValidatingExcel(ExcelLoader):
    def __init__(self, excel_path: str, sheet_index=0):
        super().__init__(excel_path, sheet_index)

    def validate(self, validator: BaseValidator):
        # ToDo, fix this:
        # logging.info(f'Validating {len(self.data)} objects with {validator.__class__}')
        validator.validate_data(self.data)
        logging.debug(f'Validation Complete.')    

    def human_errors(self):
        return self.human_file_errors(self.data.get_all_errors())

    @staticmethod
    def human_file_errors(file_errors: dict) -> dict:
        errors = {}
        for row_index, row_errors in file_errors.items():
            errors.setdefault(row_index, []).extend(ValidatingExcel.human_row_errors(row_errors))
        return errors        

    @staticmethod
    def human_row_errors(row_errors: dict) -> List[str]:
        errors = []
        for entity_type, entity_errors in row_errors.items():
            errors.extend(ValidatingExcel.human_entity_errors(entity_type, entity_errors))
        return errors

    @staticmethod
    def human_entity_errors(entity_type: str, entity_errors: dict) -> List[str]:
        errors = []
        for attribute_name, attribute_errors in entity_errors.items():
            errors.extend(ValidatingExcel.human_attribute_errors(entity_type, attribute_name, attribute_errors))
        return errors

    @staticmethod
    def human_attribute_errors(entity_type: str, attribute_name: str, attribute_errors: List[str]) -> List[str]:
        errors = []
        for error in attribute_errors:
            if error.startswith('should have required property'):
                message = f'Error: {entity_type} {error}'
            else:
                message = f'Error: {entity_type}.{attribute_name} {error}'
            errors.append(message)
        return errors
