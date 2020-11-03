import requests
import json
import os

from .not_known_entity_exception import NotKnownEntityException
from .validation_state import ValidationState


class ValidationService:
    SCHEMA_FILENAME_PREFIX = "covid_data_uploader-"
    SCHEMA_FILENAME_EXTENSION = ".json"
    SCHEMA_FILES_FOLDER = "../json-schema/"
    ENTITY_MAPPING_FILE = "../config/schema_by_entity_mapping.json"

    def __init__(self, validator_url):
        self.validator_url = validator_url
        self.current_folder = os.path.dirname(__file__)

    def validate_spreadsheet_json(self, valid_json_from_spreadsheet):
        validation_results = {'errors': [], 'state': ValidationState.PASS}

        errors_by_entities = {}
        for entities in valid_json_from_spreadsheet:
            row_nb = entities.get("row")
            for entity_type in entities:
                entity = entities[entity_type]

                if entity_type == "row":
                    continue

                schema_file_name = f"{self.SCHEMA_FILENAME_PREFIX}{self.get_schema_by_entity_type(entity_type)}{self.SCHEMA_FILENAME_EXTENSION}"
                with open(os.path.join(self.current_folder, f"{self.SCHEMA_FILES_FOLDER}{schema_file_name}")) as schema_file:
                    schema_by_entity_type = json.load(schema_file)
                validation_result = \
                    self.validate_by_schema(schema_by_entity_type, entity).json()

                if len(validation_result) != 0:
                    errors_by_entities[entity_type] = validation_result
            if len(errors_by_entities) != 0:
                validation_results['errors'].append({row_nb: errors_by_entities})
                validation_results['state'] = ValidationState.FAIL
            errors_by_entities = {}

        return validation_results

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

