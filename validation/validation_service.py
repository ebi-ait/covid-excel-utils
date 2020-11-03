import copy
import requests
import json
import os

from .not_known_entity_exception import NotKnownEntityException
from .validation_state import ValidationState

def translate_json_schema_error_to_human(object_name: str, schema_errors: dict):
    translated_messages = []
    for schema_error in schema_errors:
        path = schema_error['dataPath']
        for error in schema_error['errors']:
            translated_messages.append(f'Error: {object_name}{path} {error}')
    return translated_messages

class ValidationService:
    SCHEMA_FILENAME_PREFIX = "covid_data_uploader-"
    SCHEMA_FILENAME_EXTENSION = ".json"
    SCHEMA_FILES_FOLDER = "../json-schema/"
    ENTITY_MAPPING_FILE = "../config/schema_by_entity_mapping.json"

    def __init__(self, validator_url):
        self.validator_url = validator_url
        self.current_folder = os.path.dirname(__file__)

    def validate_data(self, data):
        issues = {}
        for entities in data:
            for entity_type, entity in entities.items():
                if entity_type == 'row':
                    continue
                # ToDo: These schema files never change and yet we load them from disk during every row of the excel spreadsheet!
                schema_file_name = f'{self.SCHEMA_FILENAME_PREFIX}{self.get_schema_by_entity_type(entity_type)}{self.SCHEMA_FILENAME_EXTENSION}'
                with open(os.path.join(self.current_folder, f'{self.SCHEMA_FILES_FOLDER}{schema_file_name}')) as schema_file:
                    schema = json.load(schema_file)
                
                validation_result = self.validate_by_schema(schema, entity).json()
                human_errors = translate_json_schema_error_to_human(entity_type, validation_result)
                if human_errors:
                    entity.setdefault('errors', []).extend(human_errors)
                    issues.setdefault(str(entities['row']), []).extend(human_errors)
        return issues

    def validate_by_schema(self, schema, object_to_validate):
        schema.pop('id', None)
        payload = self.__create_validator_payload(schema, object_to_validate)
        validation_response = requests.post(self.validator_url, json=payload)

        return validation_response

    def get_schema_by_entity_type(self, entity_type):
        with open(os.path.join(self.current_folder, f"{self.ENTITY_MAPPING_FILE}")) as schema_config_file:
            schema_config = json.load(schema_config_file)

        try:
            schema_name = schema_config[entity_type]
        except KeyError:
            raise NotKnownEntityException(entity_type)

        return schema_name

    @staticmethod
    def __create_validator_payload(schema, object_to_validate):
        return {
            "schema": schema,
            "object": object_to_validate
        }

