from typing import List
from biosamples_v4.api import Client as BioSamplesClient
from biosamples_v4.aap import Client as AapClient
from biosamples_v4.encoders import SampleEncoder
from biosamples_v4.models import Attribute, Sample
from excel.clean import entity_has_attribute, is_value_populated


def attribute_name(name: str) -> str:
    return name.replace('_', ' ')


def optional_attribute(sample: dict, attribute: str):
    return sample[attribute] if entity_has_attribute(sample, attribute) else None


def make_attribute(name, value) -> Attribute:
    units = None
    # ToDo: Refactor to create the Sample at validation-time so the units are accessible from validation_map
    if name in ['geographic_location_(latitude)', 'geographic_location_(longitude)']:
        units = 'DD'
    return Attribute(name=attribute_name(name), value=value, unit=units)


def make_attributes(sample: dict) -> List[Attribute]:
    attributes = []
    for name, value in sample.items():
        if is_value_populated(value):
            attributes.append(make_attribute(name, value))
    return attributes


def fixup_sample(sample: dict) -> dict:
    fixed_sample = sample.copy()
    remove_keys = ['errors', 'schema_errors', 'sample_accession', 'sample_alias', 'sample_title',
                   'sample_description', 'tax_id', 'scientific_name', 'domain']
    for key in remove_keys:
        if key in fixed_sample:
            fixed_sample.pop(key)

    if 'collecting_institution' not in fixed_sample and 'collecting_institute' in fixed_sample:
        fixed_sample['collecting_institution'] = fixed_sample.pop('collecting_institute')
    return fixed_sample


def map_sample(input_sample: dict) -> Sample:
    sample = Sample(
        accession=optional_attribute(input_sample, 'sample_accession'),
        name=optional_attribute(input_sample, 'sample_title'),
        domain=optional_attribute(input_sample, 'domain'),
        ncbi_taxon_id=optional_attribute(input_sample, 'tax_id'),
        species=optional_attribute(input_sample, 'scientific_name')
    )
    sample._append_organism_attribute()
    sample.attributes.extend(make_attributes(fixup_sample(input_sample)))
    return sample


class BioSamples:
    def __init__(self, aap_client: AapClient, url, domain):
        self.aap = aap_client
        self.biosamples = BioSamplesClient(url)
        self.domain = domain
        self.encoder = SampleEncoder()

    # ToDo: Move encoding the sample to conversion.biosamples.py
    def encode_sample(self, input_sample: dict) -> dict:
        sample = map_sample(input_sample)
        return self.encoder.default(sample)

    def send_sample(self, sample: dict):
        sample['domain'] = self.domain
        if 'accession' in sample and sample['accession']:
            return self.biosamples.update_sample(sample=sample, jwt=self.aap.get_token())
        return self.biosamples.persist_sample(sample=sample, jwt=self.aap.get_token())
