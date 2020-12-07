from services.ena_taxonomy import EnaTaxonomy
from validation.base import BaseValidator


class TaxonomyValidator(BaseValidator):
    def __init__(self, ena_url: str):
        self.ena_taxonomy = EnaTaxonomy(ena_url)

    def validate_data(self, data: dict) -> dict:
        errors = {}
        for row_index, entities in data.items():
            row_issues = {}
            for entity_type, entity in entities.items():
                if entity_type == 'sample':
                    entity_errors = self.validate_sample(entity)
                    if entity_errors:
                        row_issues[entity_type] = entity_errors
            if row_issues:
                errors[row_index] = row_issues
        return errors

    def validate_sample(self, sample):
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
            sample.setdefault('errors', {}).setdefault(attribute, []).extend(errors)
        return sample_errors
    
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
