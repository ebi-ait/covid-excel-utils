import json
from fnmatch import fnmatch
from os import listdir
from os.path import dirname, join, splitext
from typing import List

import requests


class SchemaValidation:
    schema_by_type = {}

    def __init__(self, validator_url):
        self.validator_url = validator_url
        self.__load_schema_files()

    def validate_data_for_human(self, data):
        issues = {}
        for entities in data:
            for entity_type, entity in entities.items():
                if entity_type == 'row':
                    continue
                human_errors = self.get_human_errors(entity_type, entity)
                if human_errors:
                    entity.setdefault('errors', []).extend(human_errors)
                    issues.setdefault(str(entities['row']), []).extend(human_errors)
        return issues

    def get_human_errors(self, entity_type, entity):
        validation_result = self.validate(entity_type, entity)
        return self.__translate_to_human(entity_type, validation_result)

    def validate_data(self, data):
        issues = {}
        for entities in data:
            row_issues = {}
            row_index = 0
            for entity_type, entity in entities.items():
                if entity_type == 'row':
                    row_index = entity
                entity_issues = self.validate(entity_type, entity)
                if entity_issues:
                    row_issues[entity_type] = entity_issues
            if row_issues and row_index:
                issues[row_index] = row_issues
        return issues

    def validate(self, entity_type, entity):
        schema = self.schema_by_type.get(entity_type, {})
        return self.__validate(schema, entity)

    def __validate(self, schema, entity):
        schema.pop('id', None)
        payload = self.__create_validator_payload(schema, entity)
        return requests.post(self.validator_url, json=payload).json()

    def __load_schema_files(self):
        schema_dir = join(dirname(__file__), 'schema')
        for file in listdir(schema_dir):
            if fnmatch(file, '*.json'):
                entity_type = splitext(file)[0]
                file_path = join(schema_dir, file)
                with open(file_path) as schema_file:
                    self.schema_by_type[entity_type] = json.load(schema_file)

    @staticmethod
    def __create_validator_payload(schema, entity):
        entity = json.loads(json.dumps(entity).lower())
        return {
            "schema": schema,
            "object": entity
        }

    @staticmethod
    def __translate_to_human(entity_type: str, schema_errors: dict) -> List[str]:
        translated_messages = []
        for attribute_error in schema_errors:
            translated_messages.extend(
                translate_to_human(
                    entity_type,
                    attribute_name=attribute_error['dataPath'].strip('.'),
                    attribute_errors=attribute_error['errors']
                )
            )
        return translated_messages


def translate_to_human(entity_type: str, attribute_name: str, attribute_errors: List[str]) -> List[str]:
    translated = []
    for error in attribute_errors:
        if error.startswith('should have required property'):
            message = f'Error: {entity_type} {error}'.replace('"', '\'')
        else:
            message = f'Error: {entity_type}.{attribute_name} {error}'.replace('"', '\'')
        translated.append(message)
    return translated
