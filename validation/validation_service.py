import copy
import requests
import json
import os

from .not_known_entity_exception import NotKnownEntityException


def translate_json_schema_error_to_human(object_name: str, schema_errors: dict):
    translated_messages = []
    for schema_error in schema_errors:
        path = schema_error['dataPath']
        for error in schema_error['errors']:
            translated_messages.append(f'Error: {object_name}{path} {error}')
    return translated_messages


class ValidationService:
    SCHEMA_FILENAME_EXTENSION = ".json"
    SCHEMA_FILES_FOLDER = "../json-schema/"
    ENTITY_MAPPING_FILE = "../config/schema_by_entity_mapping.json"
    ENTITY_TYPES = ['study', 'sample', 'run_experiment', 'isolate_genome_assembly_information']
    CURRENT_FOLDER = os.path.dirname(__file__)
    schema_by_type = {}

    def __init__(self, validator_url):
        self.validator_url = validator_url
        ValidationService.__load_schema_files()

    def validate_data(self, data):
        issues = {}
        for entities in data:
            for entity_type, entity in entities.items():
                if entity_type == 'row':
                    continue

                schema = self.schema_by_type[entity_type]

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

    @staticmethod
    def __create_validator_payload(schema, object_to_validate):
        #  TODO is there a better way to make it lowercase?
        object_to_validate = json.loads(json.dumps(object_to_validate).lower())
        return {
            "schema": schema,
            "object": object_to_validate
        }

    @staticmethod
    def __load_schema_files():
        for entity_type in ValidationService.ENTITY_TYPES:
            schema_file_name = \
                f'{ValidationService.get_schema_by_entity_type(entity_type)}{ValidationService.SCHEMA_FILENAME_EXTENSION}'
            with open(os.path.join(ValidationService.CURRENT_FOLDER,
                                   f'{ValidationService.SCHEMA_FILES_FOLDER}{schema_file_name}')) as schema_file:
                ValidationService.schema_by_type[entity_type] = json.load(schema_file)

    @staticmethod
    def get_schema_by_entity_type(entity_type):
        with open(os.path.join(ValidationService.CURRENT_FOLDER,
                               f"{ValidationService.ENTITY_MAPPING_FILE}")) as schema_config_file:
            schema_config = json.load(schema_config_file)

        try:
            schema_name = schema_config[entity_type]
        except KeyError:
            raise NotKnownEntityException(entity_type)

        return schema_name

