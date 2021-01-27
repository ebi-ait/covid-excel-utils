from typing import Set

EXAMPLE_ATTRIBUTES = {
    'sample_alias': 'hCoV-19/Ireland/D-NVRL-20G44567/2020',
    'tax_id': '2697049',
    'scientific_name': 'Severe acute respiratory syndrome coronavirus 2',
    'sample_title': 'Oro-Nasopharyngeal swab',
    'sample_description': 'hCov-19 ONT reads obtained following the Artic v3 protocol',
    'collection_date': '2020-03-31',
    'geographic_location_country_and_or_sea': 'Ireland',
    'host_common_name': 'Human',
    'host_sex': 'Male',
    'host_scientific_name': 'Homo sapiens',
    'submission_tool': 'drag and drop uploader tool',
    'geographic_location_latitude': '53.1424',
    'geographic_location_longitude': '7.6921',
    'geographic_location_region_and_locality': 'Europe / Ireland / County Dublin',
    'sample_capture_status': 'active surveillance in response to outbreak',
    'host_age': '81 - 90',
    'isolation_source_host-associated': 'Oro-Nasopharyngeal swab'
}


class EntityIdentifier:
    entity_type: str  # examples: project, study, sample, experiment_run
    index: str  # example: hCoV-19/Ireland/D-NVRL-20G44567/2020
    accession: str  # example: PRJEB42510

    # ToDo: Decide if we need these hash methods
    #  def __hash__(self):
    #    if self.accession:
    #        return hash((self.entity_type, self.accession))
    #    else:
    #        return hash((self.entity_type, self.index))


class Entity:
    identifier: EntityIdentifier
    attributes: dict
    links: Set[EntityIdentifier]

    #  def __hash__(self):
    #     return hash(self.identifier)
