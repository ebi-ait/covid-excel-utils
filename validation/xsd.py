from fnmatch import fnmatch
from os import listdir
from os.path import dirname, join, splitext
import re

from lxml import etree

from submission.submission import Submission
from submission.entity import Entity
from conversion.ena.submission import EnaSubmissionConverter, CONVERSION_MAP
from .base import BaseValidator


class XMLSchemaValidator(BaseValidator):
    ena_schema = {}

    def __init__(self):
        self.__load_schema_files()
        self.regex = re.compile(r'^Element \'(?P<element>.+)\':( \[(?P<type>.+)\])? (?P<error>.*)$')

    def validate_data(self, data: Submission):
        for entity_type, converter in CONVERSION_MAP:
            ena_type = converter.ena_type.upper()
            for entity in data.get_entities(entity_type):
                schema = self.ena_schema[ena_type]
                ena_set = etree.XML(f'<{ena_type}_SET />')
                ena_set.append(EnaSubmissionConverter.convert_entity(converter, data, entity))

                if not schema(ena_set):
                    self.add_errors(schema, ena_type, entity_type, entity)

    def add_errors(self, schema, ena_type: str, entity_type: str, entity: Entity):
        for error in schema.error_log:
            match = self.regex.match(error.message)
            error_message = match.group('error') if match else error.message
            error_attribute = error.path.rpartition('/')[2].lower()
            if error_attribute not in entity.attributes:
                error_attribute = f'{entity_type}_ena_{ena_type}_accession'.lower()
                error_message = f'{error.path} {error_message}'
            entity.add_error(error_attribute, error_message)

    def __load_schema_files(self):
        schema_dir = join(dirname(__file__), 'schema')
        for file in listdir(schema_dir):
            if fnmatch(file, '*.xsd'):
                ena_type = splitext(file)[0]
                self.ena_schema[ena_type] = etree.XMLSchema(etree.parse(join(schema_dir, file)))
