import json
from fnmatch import fnmatch
from os import listdir
from os.path import dirname, join, splitext

import requests
from excel.validate import ValidatedExcel
from docker_helper.docker_utils import DockerUtils

VALIDATOR_IMAGE_NAME = "dockerhub.ebi.ac.uk/ait/json-schema-validator"
VALIDATOR_PORT = 3020


class SchemaValidation:
    schema_by_type = {}

    def __init__(self, validator_url: str):
        self.validator_url = validator_url
        self.__load_schema_files()
        self.docker_utils = DockerUtils(VALIDATOR_IMAGE_NAME, VALIDATOR_PORT)

    def validate_excel(self, excel_file: ValidatedExcel):
        self.__start_json_schema_validator()
        excel_file.errors = self.validate_data(excel_file.rows)
        self.__stop_json_schema_validator()

    def validate_data(self, data: dict) -> dict:
        errors = {}
        for row_index, entities in data.items():
            row_issues = {}
            for entity_type, entity in entities.items():
                entity_issues = self.validate(entity_type, entity)
                if entity_issues:
                    row_issues[entity_type] = entity_issues
            if row_issues:
                errors[row_index] = row_issues
        return errors

    def validate(self, entity_type: str, entity: dict) -> dict:
        schema = self.schema_by_type.get(entity_type, {})
        schema_errors = self.__validate(schema, entity)
        errors = self.__translate_to_error(schema_errors)
        entity['errors'] = errors
        return errors

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
