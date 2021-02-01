from typing import NamedTuple

from lxml import etree
from xml.etree.ElementTree import Element

from submission.submission import Submission
from .base import BaseEnaConverter
from .project import EnaProjectConverter


class ConverterParams(NamedTuple):
    file_name: str
    root_node: Element
    converter: BaseEnaConverter


class EnaSubmissionConverter:
    def __init__(self):
        study_converter = EnaProjectConverter()
        # sample_converter = EnaProjectConverter()
        self.conversion_map = {
            'study': ConverterParams('projects.xml', etree.XML('<PROJECT_SET />'), study_converter),
            # 'sample': ConverterParams('samples.xml', etree.XML('<SAMPLE_SET />'), sample_converter)
        }

    def convert(self, data: Submission) -> dict:
        ena_files = {}
        params: ConverterParams  # ToDo: Upgrade python to 3.9 for dict[str, ConverterParams]
        for entity_type, params in self.conversion_map.items():
            xml_node = params.root_node
            for entity in data.get_entities(entity_type):
                xml_node.append(params.converter.convert(entity))
            ena_files[params.file_name] = xml_node

        # ToDo: Generate Submission file
        # Handle study.release_date
        return ena_files
