import json
from fnmatch import fnmatch
from os import listdir
from os.path import dirname, join, splitext

import requests
from .base import BaseValidator
from docker_helper.docker_utils import DockerUtils

VALIDATOR_IMAGE_NAME = "dockerhub.ebi.ac.uk/ait/json-schema-validator"
VALIDATOR_PORT = 3020


class SchemaValidator(BaseValidator):
    schema_by_type = {}

    def __init__(self, validator_url: str):
        self.validator_url = validator_url
        self.__load_schema_files()
        self.docker_utils = DockerUtils(VALIDATOR_IMAGE_NAME, VALIDATOR_PORT)

    def validate_data(self, data: dict) -> dict:
        self.__stop_json_schema_validator()
        errors = {}
        for row_index, entities in data.items():
            row_issues = {}
            for entity_type, entity in entities.items():
                entity_errors = self.validate_entity(entity_type, entity)
                if entity_errors:
                    row_issues[entity_type] = entity_errors
            if row_issues:
                errors[row_index] = row_issues
        self.__stop_json_schema_validator()
        return errors

    def validate_entity(self, entity_type: str, entity: dict) -> dict:
        schema = self.schema_by_type.get(entity_type, {})
        schema_errors = self.__validate(schema, entity)
        entity_errors = self.__translate_to_error(schema_errors)
        entity['errors'] = entity_errors
        return entity_errors

    def __validate(self, schema: dict, entity: dict):
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

    def __start_json_schema_validator(self):
        self.docker_utils.launch()

    def __stop_json_schema_validator(self):
        self.docker_utils.stop()

    @staticmethod
    def __create_validator_payload(schema, entity):
        entity = json.loads(json.dumps(entity).lower())
        return {
            "schema": schema,
            "object": entity
        }

    @staticmethod
    def __translate_to_error(schema_errors: dict) -> dict:
        errors = {}
        for schema_error in schema_errors:
            attribute_name = str(schema_error['dataPath']).strip('.')
            errors.setdefault(attribute_name, []).extend(schema_error['errors'])
        return errors
