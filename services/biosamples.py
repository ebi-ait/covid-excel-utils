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


# Only Suitable for COVID uses, will need to externalise to make package suitable for other purposes
def make_attribute(name, value) -> Attribute:
    iri = None
    units = None
    if name in ['host_common_name', 'host_scientific_name'] and value.lower() in ['human', 'homo sapiens']:
        iri = 'http://purl.obolibrary.org/obo/NCBITaxon_9606'
    elif name.startswith('isolation') and value.lower() == 'nasopharyngeal swab':
        iri = 'http://purl.obolibrary.org/obo/NCIT_C155831'
    elif name == 'geographic_location_(latitude)' or name == 'geographic_location_(longitude)':
        units = 'DD'
    return Attribute(name=attribute_name(name), value=value, iris=iri, unit=units)


def make_attributes(sample: dict) -> List[Attribute]:
    attributes = []
    for name, value in sample.items():
        if value_populated(value):
            attributes.append(make_attribute(name, value))
    return attributes


def fixup_sample(sample: dict):
    remove_keys = ['errors', 'sample_accession', 'sample_alias', 'sample_title', 'sample_description', 'tax_id',
                   'scientific_name', 'domain']
    for key in remove_keys:
        if key in sample:
            sample.pop(key)

    if 'collecting_institution' not in sample and 'collecting_institute' in sample:
        sample['collecting_institution'] = sample.pop('collecting_institute')


def map_sample(input_sample: dict) -> Sample:
    sample = Sample(
        accession=optional_attribute(input_sample, 'sample_accession'),
        name=optional_attribute(input_sample, 'sample_title'),
        domain=optional_attribute(input_sample, 'domain'),
        ncbi_taxon_id=optional_attribute(input_sample, 'tax_id'),
        species=optional_attribute(input_sample, 'scientific_name')
    )
    sample._append_organism_attribute()
    fixup_sample(input_sample)
    sample.attributes.extend(make_attributes(input_sample))
    return sample


class BioSamples:
    def __init__(self, aap_client: AapClient, url, domain):
        self.aap = aap_client
        self.biosamples = BioSamplesClient(url)
        self.domain = domain
        self.encoder = SampleEncoder()

    def encode_sample(self, input_sample: dict) -> dict:
        sample = map_sample(input_sample)
        return self.encoder.default(sample)

    def send_sample(self, sample: dict):
        sample['domain'] = self.domain
        if 'accession' in sample and sample['accession']:
            return self.biosamples.update_sample(sample=sample, jwt=self.aap.get_token())
        return self.biosamples.persist_sample(sample=sample, jwt=self.aap.get_token())
