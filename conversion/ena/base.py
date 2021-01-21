from copy import deepcopy

from lxml import etree
from jsonconverter.json_mapper import JsonMapper


class BaseEnaConverter():
    def __init__(self, template_path, xpath_spec):
        self.template = etree.parse(template_path).getroot()
        self.xpath_spec = xpath_spec

    def convert(self, entity: dict):
        entity_xml = deepcopy(self.template)
        xpath_map = JsonMapper(entity).map(self.xpath_spec)
        for xpath_key, value in xpath_map.items():
            # ToDo: Handle the case where the xpath_key is not found by creating the necessary element
            # We can then remove the need for template.xml files. 
            element = entity_xml.xpath(xpath_key)[0]
            if isinstance(value, dict):
                for attribute_key, attribute_value in value.items():
                    element.attrib[attribute_key] = attribute_value
            else:
                element.text = value
        return entity_xml
