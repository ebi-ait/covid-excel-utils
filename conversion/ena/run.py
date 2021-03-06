from copy import deepcopy
from xml.etree.ElementTree import Element

from lxml import etree
from submission.entity import Entity
from .base import BaseEnaConverter
from .experiment import EXPERIMENT_ACCESSION_PRIORITY

RUN_SPEC = {
    '@center_name': ['center_name'],
    'TITLE': ['experiment_name'],
    'EXPERIMENT_REF': {}
}
REMOVE_KEYS = ['experiment_accession', 'center_name', 'experiment_name', 'library_name', 'library_strategy', 'library_source', 'library_selection', 'insert_size', 'sequencing_platform', 'sequencing_instrument', 'uploaded_file_1', 'uploaded_file_2', 'uploaded_file_1_checksum', 'uploaded_file_2_checksum']


class EnaRunConverter(BaseEnaConverter):
    def __init__(self):
        super().__init__(ena_type='Run', xml_spec=RUN_SPEC)
    
    def convert(self, entity: Entity, xml_spec: dict = None) -> Element:
        if not xml_spec:
            xml_spec = deepcopy(self.xml_spec)
        if 'EXPERIMENT_REF' in xml_spec:
            BaseEnaConverter.add_link(xml_spec['EXPERIMENT_REF'], entity, EXPERIMENT_ACCESSION_PRIORITY)
        return super().convert(entity, xml_spec=xml_spec)

    @staticmethod
    def post_conversion(entity: Entity, xml_element: Element):
        data_block = etree.SubElement(xml_element, 'DATA_BLOCK')
        EnaRunConverter.add_files(entity, etree.SubElement(data_block, 'FILES'))

        attributes = etree.SubElement(xml_element, 'RUN_ATTRIBUTES')
        for key, value in entity.attributes.items():
            if key not in REMOVE_KEYS:
                BaseEnaConverter.make_attribute(attributes, 'RUN_ATTRIBUTE', key, value)
    
    @staticmethod
    def add_files(entity: Entity, xml_element: Element):
        file_number = 1
        file_key = f'uploaded_file_{file_number}'
        while file_key in entity.attributes:
            file = etree.SubElement(xml_element, 'FILE')
            file.attrib['filename'] = entity.attributes[file_key]
            file.attrib['filetype'] = EnaRunConverter.get_file_type(entity.attributes[file_key])
            file.attrib['checksum_method'] = 'MD5'
            checksum_key = file_key + '_checksum'
            if checksum_key in entity.attributes:
                file.attrib['checksum'] = entity.attributes[checksum_key]

            file_number = file_number + 1
            file_key = f'uploaded_file_{file_number}'
    
    @staticmethod
    def get_file_type(file_name: str) -> str:
        if '.bam' in file_name.lower():
            return 'bam'
        elif '.cram' in file_name.lower():
            return 'cram'
        elif '.fastq' in file_name.lower():
            return 'fastq'
