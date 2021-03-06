from copy import deepcopy
from typing import Iterable
from xml.etree.ElementTree import Element

from lxml import etree
from json_converter.json_mapper import JsonMapper
from conversion.conversion_utils import fixed_attribute

from submission.entity import Entity


class BaseEnaConverter:
    def __init__(self, ena_type: str, xml_spec: dict):
        self.ena_type = ena_type
        self.xml_spec = xml_spec

    def convert(self, entity: Entity, xml_spec: dict = None) -> Element:
        if not xml_spec:
            xml_spec = deepcopy(self.xml_spec)
        self.add_alias(xml_spec, entity)
        xml_map = JsonMapper(entity.attributes).map(xml_spec)
        root = etree.Element(self.ena_type.upper())
        self.add_children(parent=root, children=xml_map)
        self.post_conversion(entity, root)
        return root

    def add_alias(self, spec: dict, entity: Entity):
        accession = entity.get_accession(f'ENA_{self.ena_type}')
        if accession:
            spec['@accession'] = ['', fixed_attribute, accession]
        else:
            spec['@alias'] = ['', fixed_attribute, entity.identifier.index]
       
    @staticmethod
    def post_conversion(entity: Entity, xml_element: Element):
        pass
    
    @staticmethod
    def add_children(parent: Element, children: dict):
        for name, value in children.items():
            if name.startswith('@'):
                attribute_name = name.lstrip('@')
                parent.attrib[attribute_name] = str(value)
            else:
                element = etree.SubElement(parent, name)
                if isinstance(value, dict):
                    BaseEnaConverter.add_children(parent=element, children=value)
                elif value and str(value):
                    element.text = str(value)

    @staticmethod
    def make_attribute(parent: Element, element_name: str, key: str, value: str, key_name: str = None, value_name: str = None):
        attribute = etree.SubElement(parent, element_name)
        if not key_name:
            key_name = 'TAG'
        attribute_key = etree.SubElement(attribute, key_name)
        attribute_key.text = key
        
        if not value_name:
            value_name = 'VALUE'
        attribute_value = etree.SubElement(attribute, value_name)
        attribute_value.text = value

    @staticmethod
    def add_link(link: dict, entity: Entity, accession_services: Iterable[str]):
        accession = entity.get_first_accession(accession_services)
        if accession:
            link['@accession'] = ['', fixed_attribute, accession]
        else:
            link['@refname'] = ['', fixed_attribute, entity.identifier.index]
