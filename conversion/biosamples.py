from typing import Dict, List

from biosamples_v4.models import Attribute, Sample
from submission.entity import Entity

REMOVE_KEYS = ['sample_accession', 'sample_alias', 'sample_title', 'sample_description', 'tax_id', 'scientific_name', 'domain']


class BioSamplesConverter:
    def __init__(self, column_map: Dict[str, dict], domain=None):
        self.domain = domain
        self.unit_map: Dict[str, str] = {}
        for column_info in column_map.values():
            if 'units' in column_info and 'attribute' in column_info:
                self.unit_map[column_info['attribute']] = column_info['units']

    def convert_sample(self, sample_entity: Entity) -> Sample:
        sample = Sample(
            accession=sample_entity.get_accession('BioSamples'),
            name=self.named_attribute(sample_entity, 'sample_title'),
            domain=self.named_attribute(sample_entity, 'domain', self.domain),
            ncbi_taxon_id=self.named_attribute(sample_entity, 'tax_id'),
            species=self.named_attribute(sample_entity, 'scientific_name')
        )
        sample._append_organism_attribute()
        for name, value in sample_entity.attributes.items():
            if name not in REMOVE_KEYS:
                sample.attributes.append(
                    Attribute(
                        name=name.replace('_', ' '),
                        value=value,
                        unit=self.unit_map.get(name, None)
                    )
                )
        return sample

    @staticmethod
    def named_attribute(sample: Entity, attribute: str, default=None):
        return sample.attributes[attribute] if attribute in sample.attributes else default
