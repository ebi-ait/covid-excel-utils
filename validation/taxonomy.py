import logging

from services.ena_taxonomy import EnaTaxonomy
from submission.entity import Entity
from submission.submission import Submission
from validation.base import BaseValidator


class TaxonomyValidator(BaseValidator):
    def __init__(self):
        self.ena_taxonomy = EnaTaxonomy()

    def validate_data(self, data: Submission):
        entities = data.get_entities('sample')
        logging.info(f'Validating taxonomy against scientific name in {len(entities)} sample(s)')
        for entity in entities:
            self.validate_entity(entity)

    def validate_entity(self, entity: Entity):
        sample = entity.attributes
        sample_errors = {}
        if 'tax_id' in sample and 'scientific_name' in sample:
            tax_response = self.ena_taxonomy.validate_taxonomy(
                tax_id=sample['tax_id'],
                scientific_name=sample['scientific_name']
            )
            sample_errors = self.get_taxonomy_errors(tax_response)
        else:
            if 'tax_id' in sample:
                tax_response = self.ena_taxonomy.validate_tax_id(sample['tax_id'])
                sample_errors = self.get_errors(tax_response, 'tax_id')
            elif 'scientific_name' in sample:
                tax_response = self.ena_taxonomy.validate_scientific_name(sample['scientific_name'])
                sample_errors = self.get_errors(tax_response, 'scientific_name')
        for attribute, errors in sample_errors.items():
            entity.add_errors(attribute, errors)

    @staticmethod
    def get_taxonomy_errors(response: dict) -> dict:
        errors = {}
        if 'tax_id' in response:
            TaxonomyValidator.__set_errors_from_response(response['tax_id'], 'tax_id', errors)
        if 'scientific_name' in response:
            TaxonomyValidator.__set_errors_from_response(response['scientific_name'], 'scientific_name', errors)
        TaxonomyValidator.__set_errors_from_response(response, 'tax_id', errors)
        TaxonomyValidator.__set_errors_from_response(response, 'scientific_name', errors)
        return errors
    
    @staticmethod
    def get_errors(response: dict, key: str) -> dict:
        errors = {}
        TaxonomyValidator.__set_errors_from_response(response, key, errors)
        return errors

    @staticmethod
    def __set_errors_from_response(response: dict, key, errors: dict):
        if 'error' in response:
            errors.setdefault(key, []).append(response['error'])
