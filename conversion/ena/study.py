from xml.etree.ElementTree import Element

from lxml import etree
from submission.entity import Entity
from .base import BaseEnaConverter


STUDY_SPEC = {
    '@accession': ['study_accession'],
    '@alias': ['study_alias'],
    '@center_name': ['center_name'],
    'DESCRIPTOR': {
        'STUDY_TITLE': ['study_name'],
        'STUDY_DESCRIPTION': ['short_description'],
        'STUDY_ABSTRACT': ['abstract'],
        'CENTER_PROJECT_NAME': ['study_name'],
        'STUDY_TYPE': {
            '@existing_study_type': ['$object', 'Other']
        }
    }
}

REMOVE_KEYS = ['study_accession', 'study_alias', 'center_name', 'study_name', 'short_description', 'abstract', 'study_name']


class EnaStudyConverter(BaseEnaConverter):
    def __init__(self):
        super().__init__(root_name='STUDY', xml_spec=STUDY_SPEC)
    
    @staticmethod
    def post_conversion(entity: Entity, xml_element: Element):
        attributes = etree.SubElement(xml_element, 'STUDY_ATTRIBUTES')
        for key, value in entity.attributes.items():
            if key not in REMOVE_KEYS:
                super().make_attribute(attributes, 'STUDY_ATTRIBUTE', key, value)