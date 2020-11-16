from typing import List

from validation.base import BaseValidator
from .load import ExcelLoader


class ValidatingExcel(ExcelLoader):
    def __init__(self, excel_path: str, sheet_index=0):
        super().__init__(excel_path, sheet_index)
        self.errors = {}

    def validate(self, validator: BaseValidator):
        self.errors = validator.validate_data(self.rows)

    @staticmethod
    def human_entity_errors(entity_type: str, errors: dict) -> List[str]:
        translated_messages = []
        for attribute_name, attribute_errors in errors.items():
            translated_messages.extend(
                ValidatingExcel.human_attribute_errors(entity_type, attribute_name, attribute_errors))
        return translated_messages

    @staticmethod
    def human_attribute_errors(entity_type: str, attribute_name: str, attribute_errors: List[str]) -> List[str]:
        translated = []
        for error in attribute_errors:
            if error.startswith('should have required property'):
                message = f'Error: {entity_type} {error}'
            else:
                message = f'Error: {entity_type}.{attribute_name} {error}'
            translated.append(message.replace('"', '\''))
        return translated
