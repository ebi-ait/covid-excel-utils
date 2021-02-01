from xml.etree.ElementTree import Element

from lxml import etree
from json_converter.json_mapper import JsonMapper

from submission.entity import Entity


class BaseEnaConverter:
    def __init__(self, root_name: str, xml_spec: dict):
        self.root_name = root_name
        self.xml_spec = xml_spec

    def convert(self, entity: Entity) -> Element:
        xml_map = JsonMapper(entity.attributes).map(self.xml_spec)
        root = etree.Element(self.root_name)
        self.add_children(parent=root, children=xml_map)
        return root
    
    @staticmethod
    def add_children(parent: Element, children: dict):
        for name, value in children.items():
            if name.startswith('@'):
                attribute_name = name.lstrip('@')
                parent.attrib[attribute_name] = str(value)
            else:
                element = etree.Element(name)
                parent.append(element)
                if isinstance(value, dict):
                    BaseEnaConverter.add_children(parent=element, children=value)
                elif value and str(value):
                    element.text = str(value)
