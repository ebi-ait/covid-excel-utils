from http import HTTPStatus
from validation.base import BaseValidator
import requests


class TaxonomyValidator(BaseValidator):
    ENA_TAX_ID_LOOKUP_URL = 'https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/'
    ENA_SPECIES_LOOKUP_URL = "http://www.ebi.ac.uk/ena/data/taxonomy/v1/taxon/scientific-name/"
    ENTITY_NAME = 'sample'
    NOT_VALID_ERROR_MESSAGE_START = 'Not valid'
    TAX_ID_KEY = 'tax_id'
    SCIENTIFIC_NAME_KEY = 'scientific_name'

    def validate_tax_id(self, data_to_validate):
        return self.__validate(self.ENA_TAX_ID_LOOKUP_URL, 'tax_id', data_to_validate)

    def validate_scientific_name(self, data_to_validate):
        return \
            self.__validate(
                self.ENA_SPECIES_LOOKUP_URL, 'scientific_name', data_to_validate)

    def validate_data(self, data_to_validate: dict):
        errors = {}
        if 'tax_id' not in data_to_validate:
            errors['tax_id'] = "Tax_id field is mandatory."
        if 'scientific_name' not in data_to_validate:
            errors['scientific_name'] = "Scientific_name field is mandatory."
        if errors:
            return errors

        species_validation_response = \
            self.validate_scientific_name(data_to_validate['scientific_name'])
        tax_id_validation_response = self.validate_tax_id(data_to_validate['tax_id'])
        if 'error' in species_validation_response:
            self.append_value(errors, 'scientific_name', species_validation_response['error'])
        if 'error' in tax_id_validation_response:
            self.append_value(errors, 'tax_id', tax_id_validation_response['error'])

        if 'taxId' not in species_validation_response or \
                'scientificName' not in tax_id_validation_response or \
                species_validation_response['taxId'] != str(data_to_validate['tax_id']) or \
                tax_id_validation_response['scientificName'] != str(data_to_validate['scientific_name']):
            cross_check_error = f"Information is not consistent between taxId: {data_to_validate['tax_id']} " \
                                f"and scientificName: {data_to_validate['scientific_name']}"
            self.append_value(errors, 'tax_id', cross_check_error)
            self.append_value(errors, 'scientific_name', cross_check_error)

        return errors

    def __validate(self, url, data_type_to_validate, value_to_validate):
        response = self.ena_json_response(requests.get(f'{url}{value_to_validate}'),
                                          data_type_to_validate, value_to_validate)

        if isinstance(response, dict) and 'error' in response:
            return response

        if isinstance(response, list):
            response = response[0]

        if response['submittable'] == "false":
            response = \
                {'error': f'{self.NOT_VALID_ERROR_MESSAGE_START} {data_type_to_validate}: {value_to_validate}. ' \
                          f'It is not submittable.'}

        return response

    def ena_json_response(self, response, type, value):
        if not response.status_code == HTTPStatus(200):
            return {'error': f'{self.NOT_VALID_ERROR_MESSAGE_START} {type}: {value}. ' \
                             f'{response.text}'.strip()}
        if response.text == 'No results.':
            return {'error': f'{self.NOT_VALID_ERROR_MESSAGE_START} {type}: {value}'}
        return response.json()

    @staticmethod
    def append_value(dict_obj, key, value):
        if key in dict_obj:
            if not isinstance(dict_obj[key], list):
                dict_obj[key] = [dict_obj[key]]
            dict_obj[key].append(value)
        else:
            dict_obj[key] = [value]
