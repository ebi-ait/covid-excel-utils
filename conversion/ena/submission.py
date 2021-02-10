from typing import NamedTuple

from lxml import etree
from xml.etree.ElementTree import Element

from submission.submission import Submission
from .base import BaseEnaConverter
from .project import EnaProjectConverter
from .study import EnaStudyConverter
from .sample import EnaSampleConverter


class ConverterParams(NamedTuple):
    entity_type: str
    file_name: str
    root_node: Element
    converter: BaseEnaConverter


class EnaSubmissionConverter:
    def __init__(self):
        project_converter = EnaProjectConverter()
        study_converter = EnaStudyConverter()
        sample_converter = EnaSampleConverter()
        self.conversions = [
            ConverterParams('study', 'projects.xml', etree.XML('<PROJECT_SET />'), project_converter),
            ConverterParams('study', 'studies.xml', etree.XML('<STUDY_SET />'), study_converter),
            ConverterParams('sample', 'samples.xml', etree.XML('<SAMPLE_SET />'), sample_converter)
        ]

    def convert(self, data: Submission) -> dict:
        ena_files = {}
        for params in self.conversions:
            xml_node = params.root_node
            for entity in data.get_entities(params.entity_type):
                xml_node.append(params.converter.convert(entity))
            ena_files[params.file_name] = xml_node

        # ToDo: Generate Submission file
        # Handle study.release_date
        return ena_files
