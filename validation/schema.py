import json
from fnmatch import fnmatch
from os import listdir
from os.path import dirname, join, splitext

import requests
from .base import BaseValidator
from .taxonomy_validator import TaxonomyValidator


class SchemaValidator(BaseValidator):
    schema_by_type = {}

    def __init__(self, validator_url: str):
        self.validator_url = validator_url
        self.__load_schema_files()
        self.tax_id_validator = TaxonomyValidator()

    def validate_data(self, data: dict) -> dict:
        errors = {}
        for row_index, entities in data.items():
            row_issues = {}
            for entity_type, entity in entities.items():
                entity_errors = self.validate_entity(entity_type, entity)
                if entity_type == 'sample':
                    tax_id_error = \
                        self.tax_id_validator.validate_tax_id(entity['tax_id'])
                    scientific_name_error = \
                        self.tax_id_validator.validate_scientific_name(entity['scientific_name'])
                    if tax_id_error:
                        if entity_errors:
                            self.append_value(entity_errors, 'tax_id', tax_id_error)
                        else:
                            entity_errors['tax_id'] = tax_id_error
                    if scientific_name_error:
                        if entity_errors:
                            self.append_value(entity_errors, 'scientific_name', scientific_name_error)
                        else:
                            entity_errors['scientific_name'] = scientific_name_error
                if entity_errors:
                    row_issues[entity_type] = entity_errors

            if row_issues:
                errors[row_index] = row_issues
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
            stripped_errors = []
            for error in schema_error['errors']:
                stripped_errors.append(error.replace('"', '\''))
            errors.setdefault(attribute_name, []).extend(stripped_errors)
        return errors

    @staticmethod
    def append_value(dict_obj, key, value):
        # Check if key exist in dict or not
        if key in dict_obj:
            # Key exist in dict.
            # Check if type of value of key is list or not
            if not isinstance(dict_obj[key], list):
                # If type is not list then make it list
                dict_obj[key] = [dict_obj[key]]
            # Append the value in list
            dict_obj[key].append(value)
        else:
            # As key is not in dict,
            # so, add key-value pair
            dict_obj[key] = value
