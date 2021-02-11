from copy import deepcopy
from xml.etree.ElementTree import Element

from lxml import etree
from json_converter.json_mapper import JsonMapper
from json_converter.post_process import fixed_attribute  # ToDo: Add fixed attribute to json-converter.post-process

from submission.entity import Entity, EntityIdentifier


class BaseEnaConverter:
    def __init__(self, root_name: str, xml_spec: dict):
        self.root_name = root_name
        self.xml_spec = xml_spec

    def convert(self, entity: Entity, xml_spec: dict = None) -> Element:
        if not xml_spec:
            xml_spec = deepcopy(self.xml_spec)
        self.add_alias(xml_spec, entity.identifier)
        xml_map = JsonMapper(entity.attributes).map(xml_spec)
        root = etree.Element(self.root_name)
        self.add_children(parent=root, children=xml_map)
        self.post_conversion(entity, root)
        return root
    
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
    def add_alias(spec: dict, id: EntityIdentifier):
        spec['@alias'] = ['', fixed_attribute, id.index]
        if id.accession:
            spec['@accession'] = ['', fixed_attribute, id.accession]

    @staticmethod
    def add_link(link: dict, id: EntityIdentifier):
        link['@refname'] = ['', fixed_attribute, id.index]
        if id.accession:
            link['@accession'] = ['', fixed_attribute, id.accession]
