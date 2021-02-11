from xml.etree.ElementTree import Element

from lxml import etree
from submission.entity import Entity
from .base import BaseEnaConverter


SAMPLE_SPEC = {
    '@accession': ['sample_accession'],
    '@center_name': ['center_name'],
    '@broker_name': ['broker_name'],
    'TITLE': ['sample_title'],
    'SAMPLE_NAME': {
        'TAXON_ID': ['tax_id'],
        'SCIENTIFIC_NAME': ['scientific_name'],
        'COMMON_NAME': ['common_name']
    },
    'DESCRIPTION': ['sample_description']
}


REMOVE_KEYS = ['sample_accession', 'sample_alias', 'center_name', 'broker_name', 'sample_title',
               'sample_description', 'tax_id', 'scientific_name', 'common_name']


class EnaSampleConverter(BaseEnaConverter):
    def __init__(self):
        super().__init__(root_name='SAMPLE', xml_spec=SAMPLE_SPEC)

    @staticmethod
    def post_conversion(entity: Entity, xml_element: Element):
        attributes = etree.SubElement(xml_element, 'SAMPLE_ATTRIBUTES')
        for key, value in entity.attributes.items():
            if key not in REMOVE_KEYS:
                BaseEnaConverter.make_attribute(attributes, 'SAMPLE_ATTRIBUTE', key, value)
