import json
from fnmatch import fnmatch
from os import listdir
from os.path import dirname, join, splitext
from typing import Dict

import requests

from submission.entity import Entity
from .base import BaseValidator


class JsonValidator(BaseValidator):
    def __init__(self, validator_url: str):
        self.validator_url = validator_url
        self.schema_by_type = self.__load_schema_files()

    def validate_entity(self, entity: Entity):
        if entity.identifier.entity_type not in self.schema_by_type:
            return
        schema = self.schema_by_type[entity.identifier.entity_type]
        entity_string = json.dumps(entity.attributes)
        if entity.identifier.entity_type != 'run_experiment':
            entity_string = entity_string.lower()
        schema_errors = self.__validate(schema, json.loads(entity_string))
        self.__add_errors_to_entity(entity, schema_errors)

    def __validate(self, schema: dict, entity_attributes: dict):
        schema.pop('id', None)
        payload = self.__create_validator_payload(schema, entity_attributes)
        return requests.post(self.validator_url, json=payload).json()

    @staticmethod
    def __load_schema_files() -> Dict[str, dict]:
        schema_by_type = {}
        schema_dir = join(dirname(__file__), 'schema')
        for file in listdir(schema_dir):
            if fnmatch(file, '*.json'):
                entity_type = splitext(file)[0]
                file_path = join(schema_dir, file)
                with open(file_path) as schema_file:
                    schema_by_type[entity_type] = json.load(schema_file)
        return schema_by_type

    @staticmethod
    def __create_validator_payload(schema: dict, entity_attributes: dict):
        return {
            "schema": schema,
            "object": entity_attributes
        }

    @staticmethod
    def __add_errors_to_entity(entity: Entity, schema_errors: dict):
        for schema_error in schema_errors:
            attribute_name = str(schema_error['dataPath']).strip('.')
            stripped_errors = []
            for error in schema_error['errors']:
                error.replace('"', '\'')
                if error == 'should NOT be valid':
                    error = JsonValidator.__improve_not_be_valid_error_message(entity.identifier.entity_type, attribute_name)
                stripped_errors.append(error)
            entity.add_errors(attribute_name, stripped_errors)

    @staticmethod
    def __improve_not_be_valid_error_message(entity_type, attribute_name):
        return f'{entity_type} should have required property: \'{attribute_name}\''