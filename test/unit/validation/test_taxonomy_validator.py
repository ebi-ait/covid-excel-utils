import unittest
from unittest.mock import MagicMock

from validation.taxonomy import TaxonomyValidator
from submission.entity import Entity


class TestTaxonomyValidator(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.taxonomy_validator = TaxonomyValidator()
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
        # Given
        sample_attributes = {
            'scientific_name': 'Severe acute respiratory syndrome coronavirus 2',
            'tax_id': '2697049'
        }
        self.taxonomy_validator.ena_taxonomy.validate_scientific_name = MagicMock(return_value=self.valid_sarscov2)
        self.taxonomy_validator.ena_taxonomy.validate_tax_id = MagicMock(return_value=self.valid_sarscov2)
        sample = Entity('sample', 'sample1', '', sample_attributes)

        # When
        self.taxonomy_validator.validate_entity(sample)

        # Then
        self.assertFalse(sample.errors)
        self.assertDictEqual({}, sample.errors)
    
    def test_valid_sample_tax_id_should_not_return_error(self):
        # Given
        sample_attributes = {
            'tax_id': '2697049'
        }
        self.taxonomy_validator.ena_taxonomy.validate_tax_id = MagicMock(return_value=self.valid_sarscov2)
        sample = Entity('sample', 'sample1', '', sample_attributes)

        # When
        self.taxonomy_validator.validate_entity(sample)

        # Then
        self.assertFalse(sample.errors)
        self.assertDictEqual({}, sample.errors)
    
    def test_valid_sample_name_should_not_return_error(self):
        # Given
        sample_attributes = {
            'scientific_name': 'Severe acute respiratory syndrome coronavirus 2'
        }
        self.taxonomy_validator.ena_taxonomy.validate_scientific_name = MagicMock(return_value=self.valid_sarscov2)
        sample = Entity('sample', 'sample1', '', sample_attributes)

        # When
        self.taxonomy_validator.validate_entity(sample)

        # Then
        self.assertFalse(sample.errors)
        self.assertDictEqual({}, sample.errors)
    
    def test_inconsistent_sample_should_return_error(self):
        # Given
        sample_attributes = {
            'scientific_name': 'Severe acute respiratory syndrome coronavirus 2',
            'tax_id': '9606'
        }
        self.taxonomy_validator.ena_taxonomy.validate_scientific_name = MagicMock(return_value=self.valid_sarscov2)
        self.taxonomy_validator.ena_taxonomy.validate_tax_id = MagicMock(return_value=self.valid_human)
        consistent_error = 'Information is not consistent between taxId: 9606 and scientificName: Severe acute respiratory syndrome coronavirus 2'
        expected_errors = {
            'scientific_name': [consistent_error],
            'tax_id': [consistent_error]
        }
        
        sample = Entity('sample', 'sample1', '', sample_attributes)

        # When
        self.taxonomy_validator.validate_entity(sample)

        # Then
        self.assertTrue(sample.errors)
        self.assertDictEqual(expected_errors, sample.errors)

    def test_invalid_sample_tax_id_should_return_error(self):
        # Given
        sample_attributes = {
            'scientific_name': 'Severe acute respiratory syndrome coronavirus 2',
            'tax_id': '999999999999'
        }
        error = 'Not valid tax_id: 999999999999.'
        consistent_error = 'Information is not consistent between taxId: 999999999999 and scientificName: Severe acute respiratory syndrome coronavirus 2'
        expected_errors = {
            'scientific_name': [consistent_error],
            'tax_id': [error, consistent_error]
        }
        
        self.taxonomy_validator.ena_taxonomy.validate_scientific_name = MagicMock(return_value=self.valid_sarscov2)
        self.taxonomy_validator.ena_taxonomy.validate_tax_id = MagicMock(return_value={'error': error})
        
        sample = Entity('sample', 'sample1', '', sample_attributes)

        # When
        self.taxonomy_validator.validate_entity(sample)

        # Then
        self.assertTrue(sample.errors)
        self.assertDictEqual(expected_errors, sample.errors)
    
    def test_invalid_tax_id_should_return_error(self):
        # Given
        sample_attributes = {'tax_id': '999999999999'}
        error = 'Not valid tax_id: 999999999999.'
        expected_error = {
            'tax_id': [error]
        }
        self.taxonomy_validator.ena_taxonomy.validate_tax_id = MagicMock(return_value={'error': error})
        sample = Entity('sample', 'sample1', '', sample_attributes)

        # When
        self.taxonomy_validator.validate_entity(sample)

        # Then
        self.assertTrue(sample.errors)
        self.assertDictEqual(expected_error, sample.errors)

    def test_invalid_sample_name_should_return_error(self):
        # Given
        sample_attributes = {
            'scientific_name': 'Lorem Ipsum',
            'tax_id': '2697049'
        }
        error = 'Not valid scientific_name: Lorem Ipsum.'
        consistent_error = 'Information is not consistent between taxId: 2697049 and scientificName: Lorem Ipsum'
        expected_errors = {
            'scientific_name': [error, consistent_error],
            'tax_id': [consistent_error]
        }
        self.taxonomy_validator.ena_taxonomy.validate_scientific_name = MagicMock(return_value={'error': error})
        self.taxonomy_validator.ena_taxonomy.validate_tax_id = MagicMock(return_value=self.valid_sarscov2)
        
        sample = Entity('sample', 'sample1', '', sample_attributes)
        
        # When
        self.taxonomy_validator.validate_entity(sample)

        # Then
        self.assertTrue(sample.errors)
        self.assertDictEqual(expected_errors, sample.errors)

    def test_invalid_name_should_return_error(self):
        sample_attributes = {'scientific_name': 'Lorem Ipsum'}
        error = 'Not valid scientific_name: Lorem Ipsum.'
        expected_error = {
            'scientific_name': [error]
        }
        self.taxonomy_validator.ena_taxonomy.validate_scientific_name = MagicMock(return_value={'error': error})

        sample = Entity('sample', 'sample1', '', sample_attributes)
        
        # When
        self.taxonomy_validator.validate_entity(sample)

        # Then
        self.assertTrue(sample.errors)
        self.assertDictEqual(expected_error, sample.errors)


if __name__ == '__main__':
    unittest.main()
