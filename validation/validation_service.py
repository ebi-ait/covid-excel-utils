import requests


class ValidationService:

    def __init__(self, validator_url):
        self.validator_url = validator_url

    def validate(self, schema, object_to_validate):
        payload = self.__create_validator_payload(schema, object_to_validate)
        validation_response = requests.post(self.validator_url, json=payload)

        return validation_response

    @staticmethod
    def __create_validator_payload(schema, object_to_validate):
        return {
            "schema": schema,
            "object": object_to_validate
        }
