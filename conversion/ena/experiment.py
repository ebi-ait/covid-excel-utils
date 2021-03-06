from copy import deepcopy
from xml.etree.ElementTree import Element

from lxml import etree
from conversion.conversion_utils import fixed_attribute
from submission.entity import Entity
from .base import BaseEnaConverter
from .sample import SAMPLE_ACCESSION_PRIORITY
from .study import STUDY_ACCESSION_PRIORITY

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
                'SINGLE': ['', fixed_attribute, '']
            }  # , 'LIBRARY_CONSTRUCTION_PROTOCOL': ''
        }
    },
    'PLATFORM': {
        'sequencing_platform': {
            'INSTRUMENT_MODEL': ['sequencing_instrument']
        }
    }
}
EXPERIMENT_ACCESSION_PRIORITY = ['ENA_Experiment']
REMOVE_KEYS = ['experiment_accession', 'center_name', 'experiment_name', 'library_name', 'library_strategy', 'library_source', 'library_selection', 'insert_size', 'sequencing_platform', 'sequencing_instrument', 'uploaded_file_1', 'uploaded_file_2', 'uploaded_file_1_checksum', 'uploaded_file_2_checksum']


class EnaExperimentConverter(BaseEnaConverter):
    def __init__(self):
        super().__init__(ena_type='Experiment', xml_spec=EXPERIMENT_SPEC)
    
    def convert_experiment(self, experiment: Entity, sample: Entity, study: Entity) -> Element:
        spec = deepcopy(self.xml_spec)
        
        BaseEnaConverter.add_link(spec['DESIGN']['SAMPLE_DESCRIPTOR'], sample, SAMPLE_ACCESSION_PRIORITY)
        BaseEnaConverter.add_link(spec['STUDY_REF'], study, STUDY_ACCESSION_PRIORITY)

        if EnaExperimentConverter.is_paired_fastq(experiment):
            del spec['DESIGN']['LIBRARY_DESCRIPTOR']['LIBRARY_LAYOUT']['SINGLE']
        else:
            del spec['DESIGN']['LIBRARY_DESCRIPTOR']['LIBRARY_LAYOUT']['PAIRED']
        
        if 'sequencing_platform' in experiment.attributes:
            spec['PLATFORM'][experiment.attributes['sequencing_platform']] = spec['PLATFORM'].pop('sequencing_platform')
        else:
            del spec['PLATFORM']
        
        return super().convert(entity=experiment, xml_spec=spec)

    @staticmethod
    def is_paired_fastq(experiment: Entity) -> bool:
        return 'insert_size' in experiment.attributes and \
            'uploaded_file_2' in experiment.attributes and \
            'fastq' in experiment.attributes['uploaded_file_1'].lower() and \
            'fastq' in experiment.attributes['uploaded_file_2'].lower()

    @staticmethod
    def post_conversion(entity: Entity, xml_element: Element):
        attributes = etree.SubElement(xml_element, 'EXPERIMENT_ATTRIBUTES')
        for key, value in entity.attributes.items():
            if key not in REMOVE_KEYS:
                BaseEnaConverter.make_attribute(attributes, 'EXPERIMENT_ATTRIBUTE', key, value)
