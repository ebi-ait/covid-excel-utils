from typing import List
from biosamples_v4.api import Client as BioSamplesClient
from biosamples_v4.aap import Client as AapClient
from biosamples_v4.encoders import SampleEncoder
from biosamples_v4.models import Attribute, Sample
from excel.clean import object_has_attribute, value_populated


def attribute_name(name: str) -> str:
    return name.replace('_', ' ')


def optional_attribute(sample: dict, attribute: str):
    return sample[attribute] if object_has_attribute(sample, attribute) else None


def make_attributes(sample: dict) -> List[Attribute]:
    attributes = []
    for attribute, value in sample.items():
        if value_populated(value):
            attributes.append(Attribute(name=attribute_name(attribute), value=value))
    return attributes


def fixup_sample(sample: dict):
    remove_keys = ['sample_accession', 'sample_alias', 'sample_title', 'sample_description', 'tax_id',
                   'scientific_name', 'domain']
    for key in remove_keys:
        if key in sample:
            sample.pop(key)

    if 'collecting_institution' not in sample and 'collecting_institute' in sample:
        sample['collecting_institution'] = sample.pop('collecting_institute')


def map_sample(input_sample: dict) -> Sample:
    accession = optional_attribute(input_sample, 'sample_accession')
    name = optional_attribute(input_sample, 'sample_title')
    ncbi_taxon_id = optional_attribute(input_sample, 'tax_id')
    species = optional_attribute(input_sample, 'scientific_name')
    fixup_sample(input_sample)

    sample = Sample(
        accession=accession,
        name=name,
        ncbi_taxon_id=ncbi_taxon_id,
        species=species
    )
    sample._append_organism_attribute()
    sample.attributes.extend(make_attributes(input_sample))
    return sample


class BioSamples:
    def __init__(self, biosamples_url, aap_url, aap_username, aap_password):
        self.aap = AapClient(
            url=aap_url,
            username=aap_username,
            password=aap_password
        )
        self.biosamples = BioSamplesClient(biosamples_url)
        self.encoder = SampleEncoder()

    def encode_sample(self, input_sample: dict) -> dict:
        sample = map_sample(input_sample)
        return self.encoder.default(sample)

    def send_sample(self, sample: dict):
        if 'accession' in sample:
            return self.biosamples.update_sample(sample=sample, jwt=self.aap.get_token())
        return self.biosamples.persist_sample(sample=sample, jwt=self.aap.get_token())
