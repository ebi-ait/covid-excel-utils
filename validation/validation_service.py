import json
import os
import requests


def translate_json_schema_error_to_human(object_name: str, schema_errors: dict):
    translated_messages = []
    for schema_error in schema_errors:
        path = schema_error['dataPath']
        for error in schema_error['errors']:
            translated_messages.append(f'Error: {object_name}{path} {error}')
    return translated_messages


class ValidationService:
    schema_by_type = {}

    def __init__(self, validator_url):
        self.validator_url = validator_url
        self.__load_schema_files()

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

    def __load_schema_files(self):
        types = ['study', 'sample', 'run_experiment', 'isolate_genome_assembly_information']
        for entity_type in types:
            schema_path = os.path.join(os.path.dirname(__file__), 'schema', f'{entity_type}.json')
            with open(os.path.abspath(schema_path)) as schema_file:
                self.schema_by_type[entity_type] = json.load(schema_file)

    @staticmethod
    def __create_validator_payload(schema, object_to_validate):
        #  TODO is there a better way to make it lowercase?
        object_to_validate = json.loads(json.dumps(object_to_validate).lower())
        return {
            "schema": schema,
            "object": object_to_validate
        }
