import json
from http import HTTPStatus

from requests import HTTPError

from validation.base import BaseValidator

import requests


class TaxonomyValidator(BaseValidator):
    ENA_TAX_ID_LOOKUP_URL = 'https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/'
    ENA_SPECIES_LOOKUP_URL = "http://www.ebi.ac.uk/ena/data/taxonomy/v1/taxon/scientific-name/"
    ENTITY_NAME = 'sample'
    NOT_VALID_ERROR_MESSAGE_START = 'Not valid'
    TAX_ID_KEY = 'tax_id'
    SCIENTIFIC_NAME_KEY = 'scientific_name'

    def validate_tax_id(self, tax_id):
        return self.validate_data({self.TAX_ID_KEY: tax_id})

    def validate_scientific_name(self, scientific_name):
        return self.validate_data({self.SCIENTIFIC_NAME_KEY: scientific_name})

    def validate_data(self, data_to_validate: dict):
        errors = {}
        data_type_to_validate = list(data_to_validate.keys())[0]
        if data_type_to_validate == self.TAX_ID_KEY:
            validation_service_url = self.ENA_TAX_ID_LOOKUP_URL
        elif data_type_to_validate == self.SCIENTIFIC_NAME_KEY:
            validation_service_url = self.ENA_SPECIES_LOOKUP_URL
        else:
            return [f'Not valid taxonomy validation type: {data_type_to_validate}']
        validation_response = self.__validate(validation_service_url, data_to_validate)
        if validation_response:
            errors = [validation_response]

        return errors

    def __validate(self, url, data_to_validate):
        data_type_to_validate = list(data_to_validate.keys())[0]
        value_to_validate = list(data_to_validate.values())[0]
        response = self.ena_json_response(requests.get(f'{url}{value_to_validate}'),
                                          data_type_to_validate, value_to_validate)

        if isinstance(response, str) and response.startswith(self.NOT_VALID_ERROR_MESSAGE_START):
            return response

        if isinstance(response, list):
            response = response[0]

        if response['submittable'] == "false":
            response = \
                f'{self.NOT_VALID_ERROR_MESSAGE_START} {data_type_to_validate}: {value_to_validate}. ' \
                f'It is not submittable.'
        else:
            response = ""

        return response

    def ena_json_response(self, response, type, value):
        if not response.status_code == HTTPStatus(200):
            return f'{self.NOT_VALID_ERROR_MESSAGE_START} {type}: {value}. ' \
                   f'{response.text}'.strip()
        if response.text == 'No results.':
            # raise HTTPError(f'404 Client Error: No Results at: {response.url}', response)
            return f'{self.NOT_VALID_ERROR_MESSAGE_START} {type}: {value}'
        return response.json()
