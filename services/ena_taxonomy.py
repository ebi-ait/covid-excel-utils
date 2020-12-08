from http import HTTPStatus
import requests


class EnaTaxonomy:
    TAX_ID_KEY = 'tax_id'
    SPECIES_KEY = 'scientific_name'

    def __init__(self, ena_url='https://www.ebi.ac.uk/ena'):
        self.tax_id_url = f'{ena_url.rstrip("/")}/taxonomy/rest/tax-id/'
        self.species_url = f'{ena_url.rstrip("/")}/data/taxonomy/v1/taxon/scientific-name/'

    def validate_tax_id(self, tax_id: str):
        return self.__validate(self.tax_id_url, self.TAX_ID_KEY, tax_id)

    def validate_scientific_name(self, scientific_name: str):
        return self.__validate(self.species_url, self.SPECIES_KEY, scientific_name)

    def validate_taxonomy(self, scientific_name: str, tax_id: str):
        species_response = self.validate_scientific_name(scientific_name)
        tax_id_response = self.validate_tax_id(tax_id)
        response = {
            self.SPECIES_KEY: species_response,
            self.TAX_ID_KEY: tax_id_response
        }
        if 'taxId' not in species_response or 'scientificName' not in tax_id_response or \
                species_response['taxId'] != tax_id or \
                tax_id_response['scientificName'] != scientific_name:
            response['error'] = f"Information is not consistent between taxId: {tax_id} and scientificName: {scientific_name}"
        return response

    @staticmethod
    def __validate(url, data_type, value):
        get_response = requests.get(f'{url.rstrip("/")}/{value}')
        json_response = EnaTaxonomy.ena_json_response(get_response, data_type, value)

        if isinstance(json_response, dict) and 'error' in json_response:
            return json_response

        if isinstance(json_response, list):
            json_response = json_response[0]
        if 'submittable' in json_response and json_response['submittable'] == "false":
            return EnaTaxonomy.format_error(data_type, value, 'It is not submittable.')
        return json_response

    @staticmethod
    def ena_json_response(response, data_type, value) -> dict:
        if not response.status_code == HTTPStatus(200):
            return EnaTaxonomy.format_error(data_type, value, response.text.strip())
        if response.text == 'No results.':
            return EnaTaxonomy.format_error(data_type, value)
        return response.json()

    @staticmethod
    def format_error(data_type: str, value: str, details: str = None) -> dict:
        error_msg = f'Not valid {data_type}: {value}.'
        if details:
            error_msg = f'{error_msg} {details}'
        return {'error': error_msg}
