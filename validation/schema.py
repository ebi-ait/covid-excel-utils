import json
from fnmatch import fnmatch
from os import listdir
from os.path import dirname, join, splitext

import requests

from submission.entity import Entity
from .base import BaseValidator


class SchemaValidator(BaseValidator):
    schema_by_type = {}

    def __init__(self, validator_url: str):
        self.validator_url = validator_url
        self.__load_schema_files()

    def validate_entity(self, entity: Entity):
        if entity.identifier.entity_type not in self.schema_by_type:
            return
        schema = self.schema_by_type[entity.identifier.entity_type]
        schema_errors = self.__validate(schema, entity.attributes)
        self.__add_errors_to_entity(entity, schema_errors)

    def __validate(self, schema: dict, entity_attributes: dict):
        schema.pop('id', None)
        payload = self.__create_validator_payload(schema, entity_attributes)
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
    def __create_validator_payload(schema: dict, entity_attributes: dict):
        entity = json.loads(json.dumps(entity_attributes).lower())
        return {
            "schema": schema,
            "object": entity
        }

    @staticmethod
    def __add_errors_to_entity(entity: Entity, schema_errors: dict):
        for schema_error in schema_errors:
            attribute_name = str(schema_error['dataPath']).strip('.')
            stripped_errors = []
            for error in schema_error['errors']:
                stripped_errors.append(error.replace('"', '\''))
            entity.add_errors(attribute_name, stripped_errors)
