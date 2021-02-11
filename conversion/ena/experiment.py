from copy import deepcopy
from xml.etree.ElementTree import Element
from json_converter.post_process import fixed_attribute

from lxml import etree
from submission.entity import Entity
from .base import BaseEnaConverter


EXPERIMENT_SPEC = {
    '@center_name': ['center_name'],
    'TITLE': ['experiment_name'],
    'STUDY_REF': {},
    'DESIGN': {
        'DESIGN_DESCRIPTION': ['experiment_name'],
        'SAMPLE_DESCRIPTOR': {},
        'LIBRARY_DESCRIPTOR': {
            'LIBRARY_NAME': ['library_name'],
            'LIBRARY_STRATEGY': ['library_strategy'],
            'LIBRARY_SOURCE': ['library_source'],
            'LIBRARY_SELECTION': ['library_selection'],
            'LIBRARY_LAYOUT': {
                'PAIRED': {
                    'NOMINAL_LENGTH': ['insert_size']
                },
                'SINGLE': ['$object', {}]
            }  # , 'LIBRARY_CONSTRUCTION_PROTOCOL': ''
        }
    },
    'PLATFORM': {
        'sequencing_platform': {
            'INSTRUMENT_MODEL': ['sequencing_instrument']
        }
    }
}


REMOVE_KEYS = ['experiment_accession', 'center_name', 'experiment_name', 'library_name', 'library_strategy', 'library_source', 'library_selection', 'insert_size', 'sequencing_platform', 'sequencing_instrument', 'uploaded_file_1', 'uploaded_file_2']


class EnaExperimentConverter(BaseEnaConverter):
    def __init__(self):
        super().__init__(root_name='EXPERIMENT', xml_spec=EXPERIMENT_SPEC)
    
    def convert_experiment(self, experiment: Entity, sample: Entity, study: Entity) -> Element:
        spec = deepcopy(self.xml_spec)
        
        spec['DESIGN']['SAMPLE_DESCRIPTOR']['@refname'] = ['', fixed_attribute, sample.identifier.index]
        if sample.identifier.accession:
            spec['DESIGN']['SAMPLE_DESCRIPTOR']['@accession'] = ['', fixed_attribute, sample.identifier.accession]

        spec['STUDY_REF']['@refname'] = ['', fixed_attribute, study.identifier.index]
        if study.identifier.accession:
            spec['STUDY_REF']['@accession'] = ['', fixed_attribute, study.identifier.accession]

        if 'insert_size' in experiment.attributes and 'uploaded_file_2' in experiment.attributes:
            del spec['DESIGN']['LIBRARY_DESCRIPTOR']['LIBRARY_LAYOUT']['SINGLE']
        else:
            del spec['DESIGN']['LIBRARY_DESCRIPTOR']['LIBRARY_LAYOUT']['PAIRED']
        
        if 'sequencing_platform' in experiment.attributes:
            spec['PLATFORM'][experiment.attributes['sequencing_platform']] = spec['PLATFORM'].pop('sequencing_platform')
        else:
            del spec['PLATFORM']
        
        return super().convert(entity=experiment, xml_spec=spec)

    @staticmethod
    def post_conversion(entity: Entity, xml_element: Element):
        attributes = etree.SubElement(xml_element, 'EXPERIMENT_ATTRIBUTES')
        for key, value in entity.attributes.items():
            if key not in REMOVE_KEYS:
                BaseEnaConverter.make_attribute(attributes, 'EXPERIMENT_ATTRIBUTE', key, value)
