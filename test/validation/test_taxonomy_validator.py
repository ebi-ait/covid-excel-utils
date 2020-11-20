import unittest
from http import HTTPStatus
from unittest.mock import patch

from validation.taxonomy_validator import TaxonomyValidator


class TestTaxIDValidator(unittest.TestCase):

    def setUp(self):
        self.taxonomy_validator = TaxonomyValidator()

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_tax_id_not_numeric_should_return_error(self, mock_get):
        non_existing_tax_id = "NOT_NUMERIC_TAX_ID"
        taxonomy_type_to_validate = 'tax_id'
        data_to_validate = {taxonomy_type_to_validate: non_existing_tax_id}
        response_message = 'Taxon Id must be numeric.'
        expected_error_message = f'Not valid tax_id: {non_existing_tax_id}. Taxon Id must be numeric.'

        mock_get.return_value.status_code = HTTPStatus(400)
        mock_get.return_value.text = response_message

        error_result = self.taxonomy_validator.validate_data(data_to_validate)

        self.assertEqual(expected_error_message, error_result[0])

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_invalid_tax_id_given_should_return_error(self, mock_get):
        non_existing_tax_id = "999999999999"
        taxonomy_type_to_validate = 'tax_id'
        data_to_validate = {taxonomy_type_to_validate: non_existing_tax_id}
        no_results_message = 'No results.'
        expected_error_message = f'Not valid tax_id: {non_existing_tax_id}'

        mock_get.return_value.status_code = HTTPStatus(200)
        mock_get.return_value.text = no_results_message

        error_result = self.taxonomy_validator.validate_data(data_to_validate)

        self.assertEqual(expected_error_message, error_result[0])

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_valid_but_not_submittable_tax_id_given_should_return_error(self, mock_get):
        valid_tax_id = "1234"
        taxonomy_type_to_validate = 'tax_id'
        data_to_validate = {taxonomy_type_to_validate: valid_tax_id}
        results_message = {
          "taxId": "1234",
          "scientificName": "Nitrospira",
          "formalName": "false",
          "rank": "genus",
          "division": "PRO",
          "lineage": "Bacteria; Nitrospirae; Nitrospirales; Nitrospiraceae; ",
          "geneticCode": "11",
          "submittable": "false"
        }
        expected_error_message = f'Not valid tax_id: {valid_tax_id}. It is not submittable.'

        mock_get.return_value.status_code = HTTPStatus(200)
        mock_get.return_value.json.return_value = results_message

        error_result = self.taxonomy_validator.validate_data(data_to_validate)

        self.assertEqual(expected_error_message, error_result[0])

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_valid_and_submittable_tax_id_given_should_not_return_error(self, mock_get):
        valid_tax_id = "5678"
        taxonomy_type_to_validate = 'tax_id'
        data_to_validate = {taxonomy_type_to_validate: valid_tax_id}
        results_message = {
          "taxId": "5678",
          "scientificName": "Leishmania naiffi",
          "formalName": "true",
          "rank": "species",
          "division": "INV",
          "lineage": "Eukaryota; Discoba; Euglenozoa; Kinetoplastea; Metakinetoplastina; Trypanosomatida; Trypanosomatidae; Leishmaniinae; Leishmania; Leishmania naiffi species complex; ",
          "geneticCode": "1",
          "mitochondrialGeneticCode": "4",
          "plastIdGeneticCode": "11",
          "submittable": "true"
        }

        mock_get.return_value.status_code = HTTPStatus(200)
        mock_get.return_value.json.return_value = results_message

        error_result = self.taxonomy_validator.validate_data(data_to_validate)

        self.assertFalse(bool(error_result))

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_invalid_taxonomy_validation_type_given_should_return_error(self, mock_get):
        non_existing_scientific_name = "NOT VALID SCIENTIFIC NAME"
        taxonomy_type_to_validate = 'not valid taxonomy type'
        data_to_validate = {taxonomy_type_to_validate: non_existing_scientific_name}
        no_results_message = 'No results.'
        expected_error_message = f'Not valid taxonomy validation type: {taxonomy_type_to_validate}'

        mock_get.return_value.status_code = HTTPStatus(200)
        mock_get.return_value.text = no_results_message

        error_result = self.taxonomy_validator.validate_data(data_to_validate)

        self.assertEqual(expected_error_message, error_result[0])

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_not_suitable_parameter_given_should_return_error(self, mock_get):
        invalid_param = "?"
        taxonomy_type_to_validate = 'scientific_name'
        data_to_validate = {taxonomy_type_to_validate: invalid_param}
        response_message = ''
        expected_error_message = f'Not valid scientific_name: {invalid_param}.'

        mock_get.return_value.status_code = HTTPStatus(404)
        mock_get.return_value.text = response_message

        error_result = self.taxonomy_validator.validate_data(data_to_validate)

        self.assertEqual(expected_error_message, error_result[0])

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_invalid_scientific_name_given_should_return_error(self, mock_get):
        non_existing_scientific_name = "NOT VALID SCIENTIFIC NAME"
        taxonomy_type_to_validate = 'scientific_name'
        data_to_validate = {taxonomy_type_to_validate: non_existing_scientific_name}
        no_results_message = 'No results.'
        expected_error_message = f'Not valid scientific_name: {non_existing_scientific_name}'

        mock_get.return_value.status_code = HTTPStatus(200)
        mock_get.return_value.text = no_results_message

        error_result = self.taxonomy_validator.validate_data(data_to_validate)

        self.assertEqual(expected_error_message, error_result[0])

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_valid_but_not_submittable_scientific_name_given_should_return_error(self, mock_get):
        valid_scientific_name = "primates"
        taxonomy_type_to_validate = 'scientific_name'
        data_to_validate = {taxonomy_type_to_validate: valid_scientific_name}
        results_message = [
          {
            "taxId": "9443",
            "scientificName": "Primates",
            "formalName": "false",
            "rank": "order",
            "division": "MAM",
            "lineage": "Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; Euteleostomi; Mammalia; Eutheria; Euarchontoglires; ",
            "geneticCode": "1",
            "mitochondrialGeneticCode": "2",
            "submittable": "false"
          }
        ]
        expected_error_message = f'Not valid scientific_name: {valid_scientific_name}. It is not submittable.'

        mock_get.return_value.status_code = HTTPStatus(200)
        mock_get.return_value.json.return_value = results_message

        error_result = self.taxonomy_validator.validate_data(data_to_validate)

        self.assertEqual(expected_error_message, error_result[0])

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_valid_and_submittable_scientific_name_given_should_not_return_error(self, mock_get):
        valid_scientific_name = "homo sapiens"
        taxonomy_type_to_validate = 'scientific_name'
        data_to_validate = {taxonomy_type_to_validate: valid_scientific_name}
        results_message = [
          {
            "taxId": "9606",
            "scientificName": "Homo sapiens",
            "commonName": "human",
            "formalName": "true",
            "rank": "species",
            "division": "HUM",
            "lineage": "Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; Euteleostomi; Mammalia; Eutheria; Euarchontoglires; Primates; Haplorrhini; Catarrhini; Hominidae; Homo; ",
            "geneticCode": "1",
            "mitochondrialGeneticCode": "2",
            "submittable": "true"
          }
        ]

        mock_get.return_value.status_code = HTTPStatus(200)
        mock_get.return_value.json.return_value = results_message

        error_result = self.taxonomy_validator.validate_data(data_to_validate)

        self.assertFalse(bool(error_result))
