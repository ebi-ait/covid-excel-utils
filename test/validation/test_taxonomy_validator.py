import unittest
from http import HTTPStatus
from unittest.mock import patch, MagicMock

from validation.taxonomy_validator import TaxonomyValidator


class TestTaxonomyValidator(unittest.TestCase):

    TAX_ID_KEY = 'tax_id'
    SCIENTIFIC_NAME_KEY = 'scientific_name'

    def setUp(self):
        self.taxonomy_validator = TaxonomyValidator()

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_only_tax_id_given_should_return_error(self, mock_get):
        valid_tax_id = "1234"
        data_to_validate = {self.TAX_ID_KEY: valid_tax_id}
        expected_error_message = {'scientific_name': 'Scientific_name field is mandatory.'}

        error_result = self.taxonomy_validator.validate_data(data_to_validate)

        self.assertEqual(expected_error_message, error_result)

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_tax_id_not_numeric_should_return_error(self, mock_get):
        non_existing_tax_id = "NOT_NUMERIC_TAX_ID"
        response_message = 'Taxon Id must be numeric.'
        expected_error_message = {'error':
                                  f'Not valid tax_id: {non_existing_tax_id}. Taxon Id must be numeric.'}

        mock_get.return_value.status_code = HTTPStatus(400)
        mock_get.return_value.text = response_message

        error_result = self.taxonomy_validator.validate_tax_id(non_existing_tax_id)

        self.assertEqual(expected_error_message, error_result)

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_invalid_tax_id_given_should_return_error(self, mock_get):
        non_existing_tax_id = "999999999999"
        no_results_message = 'No results.'
        expected_error_message = {'error':
                                  f'Not valid tax_id: {non_existing_tax_id}'}

        mock_get.return_value.status_code = HTTPStatus(200)
        mock_get.return_value.text = no_results_message

        error_result = self.taxonomy_validator.validate_tax_id(non_existing_tax_id)

        self.assertEqual(expected_error_message, error_result)

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_valid_but_not_submittable_tax_id_given_should_return_error(self, mock_get):
        valid_tax_id = "1234"
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
        expected_error_message = {'error':
                                  f'Not valid tax_id: {valid_tax_id}. It is not submittable.'}

        mock_get.return_value.status_code = HTTPStatus(200)
        mock_get.return_value.json.return_value = results_message

        error_result = self.taxonomy_validator.validate_tax_id(valid_tax_id)

        self.assertEqual(expected_error_message, error_result)

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_valid_and_submittable_tax_id_given_should_not_return_error(self, mock_get):
        valid_tax_id = "5678"
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

        result = self.taxonomy_validator.validate_tax_id(valid_tax_id)

        self.assertTrue(bool(result))
        self.assertTrue('error' not in result)

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_not_suitable_parameter_given_should_return_error(self, mock_get):
        invalid_param = "?"
        response_message = ''
        expected_error_message = {'error':
                                  f'Not valid scientific_name: {invalid_param}.'}

        mock_get.return_value.status_code = HTTPStatus(404)
        mock_get.return_value.text = response_message

        error_result = self.taxonomy_validator.validate_scientific_name(invalid_param)

        self.assertEqual(expected_error_message, error_result)

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_invalid_scientific_name_given_should_return_error(self, mock_get):
        non_existing_scientific_name = "NOT VALID SCIENTIFIC NAME"
        no_results_message = 'No results.'
        expected_error_message = {'error':
                                  f'Not valid scientific_name: {non_existing_scientific_name}'}

        mock_get.return_value.status_code = HTTPStatus(200)
        mock_get.return_value.text = no_results_message

        error_result = self.taxonomy_validator.validate_scientific_name(non_existing_scientific_name)

        self.assertEqual(expected_error_message, error_result)

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_valid_but_not_submittable_scientific_name_given_should_return_error(self, mock_get):
        valid_scientific_name = "primates"
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
        expected_error_message = {'error':
                                  f'Not valid scientific_name: {valid_scientific_name}. It is not submittable.'}

        mock_get.return_value.status_code = HTTPStatus(200)
        mock_get.return_value.json.return_value = results_message

        error_result = self.taxonomy_validator.validate_scientific_name(valid_scientific_name)

        self.assertEqual(expected_error_message, error_result)

    @patch('validation.taxonomy_validator.requests.get')
    def test_when_valid_and_submittable_scientific_name_given_should_not_return_error(self, mock_get):
        valid_scientific_name = "homo sapiens"
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

        result = self.taxonomy_validator.validate_scientific_name(valid_scientific_name)

        self.assertTrue(bool(result))
        self.assertTrue('error' not in result)

    def test_when_scientific_name_and_tax_id_not_matching_should_return_error(self):
        valid_scientific_name = "homo sapiens"
        valid_tax_id = "9999"

        self.taxonomy_validator.validate_scientific_name = MagicMock(
            return_value=
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
        )
        self.taxonomy_validator.validate_tax_id = MagicMock(
            return_value=
            {
                "taxId": "9999",
                "scientificName": "Urocitellus parryii",
                "commonName": "Arctic ground squirrel",
                "formalName": "true",
                "rank": "species",
                "division": "ROD",
                "lineage": "Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; Euteleostomi; Mammalia; Eutheria; Euarchontoglires; Glires; Rodentia; Sciuromorpha; Sciuridae; Xerinae; Marmotini; Urocitellus; ",
                "geneticCode": "1",
                "mitochondrialGeneticCode": "2",
                "submittable": "true"
            }
        )
        expected_error_message = 'Information is not consistent between taxId: 9999 and scientificName: homo sapiens'

        data_to_validate = {self.TAX_ID_KEY: valid_tax_id, self.SCIENTIFIC_NAME_KEY: valid_scientific_name}

        error_result = self.taxonomy_validator.validate_data(data_to_validate)

        self.assertTrue(len(error_result) == 2)
        self.assertTrue(error_result['tax_id'], expected_error_message)
        self.assertTrue(error_result['scientific_name'], expected_error_message)

