import unittest
from unittest.mock import MagicMock

from validation.taxonomy import TaxonomyValidator


class TestTaxonomyValidator(unittest.TestCase):

    def setUp(self):
        self.taxonomy_validator = TaxonomyValidator(ena_url='')
        self.valid_human = {
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
        self.valid_sarscov2 = {
            "taxId": "2697049",
            "scientificName": "Severe acute respiratory syndrome coronavirus 2",
            "formalName": "false",
            "rank": "no rank",
            "division": "VRL",
            "lineage": "Viruses; Riboviria; Orthornavirae; Pisuviricota; Pisoniviricetes; Nidovirales; Cornidovirineae; Coronaviridae; Orthocoronavirinae; Betacoronavirus; Sarbecovirus; ",
            "geneticCode": "1",
            "submittable": "true"
        }

    def test_valid_sample_taxonomy_should_not_return_error(self):
        sample = {
            'scientific_name': 'Severe acute respiratory syndrome coronavirus 2',
            'tax_id': '2697049'
        }
        self.taxonomy_validator.ena_taxonomy.validate_scientific_name = MagicMock(return_value=self.valid_sarscov2)
        self.taxonomy_validator.ena_taxonomy.validate_tax_id = MagicMock(return_value=self.valid_sarscov2)
        
        errors = self.taxonomy_validator.validate_sample(sample)
        self.assertNotIn('errors', sample)
        self.assertEqual(errors, {})
    
    def test_valid_sample_tax_id_should_not_return_error(self):
        sample = {
            'tax_id': '2697049'
        }
        self.taxonomy_validator.ena_taxonomy.validate_tax_id = MagicMock(return_value=self.valid_sarscov2)
        
        errors = self.taxonomy_validator.validate_sample(sample)
        self.assertNotIn('errors', sample)
        self.assertEqual(errors, {})
    
    def test_valid_sample_name_should_not_return_error(self):
        sample = {
            'scientific_name': 'Severe acute respiratory syndrome coronavirus 2'
        }
        self.taxonomy_validator.ena_taxonomy.validate_scientific_name = MagicMock(return_value=self.valid_sarscov2)
        
        errors = self.taxonomy_validator.validate_sample(sample)
        self.assertNotIn('errors', sample)
        self.assertEqual(errors, {})
    
    def test_inconsistent_sample_should_return_error(self):
        sample = {
            'scientific_name': 'Severe acute respiratory syndrome coronavirus 2',
            'tax_id': '9606'
        }
        self.taxonomy_validator.ena_taxonomy.validate_scientific_name = MagicMock(return_value=self.valid_sarscov2)
        self.taxonomy_validator.ena_taxonomy.validate_tax_id = MagicMock(return_value=self.valid_human)
        expected_error = 'Information is not consistent between taxId: 9606 and scientificName: Severe acute respiratory syndrome coronavirus 2'
        expected = {'scientific_name': [expected_error], 'tax_id': [expected_error]}
        
        errors = self.taxonomy_validator.validate_sample(sample)
        self.assertIn('errors', sample)
        self.assertEqual(errors, sample['errors'])
        self.assertDictEqual(errors, expected)

    def test_invalid_sample_tax_id_should_return_error(self):
        sample = {
            'scientific_name': 'Severe acute respiratory syndrome coronavirus 2',
            'tax_id': '999999999999'
        }
        expected_error = 'Not valid tax_id: 999999999999.'
        
        self.taxonomy_validator.ena_taxonomy.validate_scientific_name = MagicMock(return_value=self.valid_sarscov2)
        self.taxonomy_validator.ena_taxonomy.validate_tax_id = MagicMock(return_value={'error': expected_error})

        errors = self.taxonomy_validator.validate_sample(sample)
        self.assertIn('errors', sample)
        self.assertEqual(errors, sample['errors'])
        self.assertIn('tax_id', errors)
        self.assertIn(expected_error, errors['tax_id'])
    
    def test_invalid_tax_id_should_return_error(self):
        sample = {'tax_id': '999999999999'}
        expected_error = 'Not valid tax_id: 999999999999.'
        
        self.taxonomy_validator.ena_taxonomy.validate_tax_id = MagicMock(return_value={'error': expected_error})

        errors = self.taxonomy_validator.validate_sample(sample)
        self.assertIn('errors', sample)
        self.assertEqual(errors, sample['errors'])
        self.assertIn('tax_id', errors)
        self.assertIn(expected_error, errors['tax_id'])

    def test_invalid_sample_name_should_return_error(self):
        sample = {
            'scientific_name': 'Lorem Ipsum',
            'tax_id': '2697049'
        }
        expected_error = 'Not valid scientific_name: Lorem Ipsum.'
        
        self.taxonomy_validator.ena_taxonomy.validate_scientific_name = MagicMock(return_value={'error': expected_error})
        self.taxonomy_validator.ena_taxonomy.validate_tax_id = MagicMock(return_value=self.valid_sarscov2)

        errors = self.taxonomy_validator.validate_sample(sample)
        self.assertIn('errors', sample)
        self.assertEqual(errors, sample['errors'])
        self.assertIn('scientific_name', errors)
        self.assertIn(expected_error, errors['scientific_name'])

    def test_invalid_name_should_return_error(self):
        sample = {'scientific_name': 'Lorem Ipsum'}
        expected_error = 'Not valid scientific_name: Lorem Ipsum.'
        
        self.taxonomy_validator.ena_taxonomy.validate_scientific_name = MagicMock(return_value={'error': expected_error})

        errors = self.taxonomy_validator.validate_sample(sample)
        self.assertIn('errors', sample)
        self.assertEqual(errors, sample['errors'])
        self.assertIn('scientific_name', errors)
        self.assertIn(expected_error, errors['scientific_name'])
