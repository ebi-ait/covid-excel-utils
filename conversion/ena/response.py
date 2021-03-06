import logging
import re
from re import Match
from io import BytesIO
from xml.etree.ElementTree import Element

from lxml import etree

from excel.submission import ExcelSubmission
from submission.entity import Entity
from submission.submission import Submission
from services.ena import EnaError


class EnaResponseConverter:
    def __init__(self):
        self.map = {
            'PROJECT': ('study', 'ENA_Project'),
            'STUDY': ('study', 'ENA_Study'),
            'SAMPLE': ('sample', 'ENA_Sample'),
            'EXPERIMENT': ('run_experiment', 'ENA_Experiment'),
            'RUN': ('run_experiment', 'ENA_Run'),
            'SUBMISSION': ('submission', 'ENA_Submission')
        }
        self.regex = re.compile(r'^In (?P<name>.+), alias:"(?P<alias>.+)", accession:"(?P<accession>.*)". (?P<message>.*)$')
    
    def convert_response_file(self, submission: Submission, ena_response_file: bytes):
        response = etree.parse(BytesIO(ena_response_file)).getroot()
        if 'success' in response.attrib and response.attrib['success'] == 'true':
            if isinstance(submission, ExcelSubmission):
                submission_entity = self.__add_excel_submission(submission, response)
            else:
                submission_entity = self.__add_submission(submission, response)
            self.__add_accessions(submission, response, submission_entity)
        self.__add_errors(submission, response)

    @staticmethod
    def __add_excel_submission(submission: ExcelSubmission, response: Element) -> Entity:
        ena_entity = list(response.iter('SUBMISSION')).pop()
        rows = submission.get_all_rows()
        min_row = min(rows)
        max_row = max(rows)
        for row in range(min_row, max_row + 1):
            entity = submission.map_row(row, 'submission', ena_entity.attrib['alias'], {})
        return entity

    @staticmethod
    def __add_submission(submission: Submission, response: Element) -> Entity:
        ena_entity = list(response.iter('SUBMISSION')).pop()
        return submission.map('submission', ena_entity.attrib['alias'], {})

    def __add_accessions(self, submission: Submission, response: Element, submission_entity: Entity):
        for ena_name, (entity_type, accession_type) in self.map.items():
            for ena_entity in response.iter(ena_name):
                index = ena_entity.attrib.get('alias', None)
                accession = ena_entity.attrib.get('accession', None)
                if index and accession:
                    entity = submission.get_entity(entity_type, index)
                    if not entity:
                        entity = submission.get_entity(entity_type, accession)
                    if not entity:
                        logging.warning(f'Cannot add find {entity_type}.{index} to add accession {accession}')
                        continue
                    entity.add_accession(accession_type, accession)
                    submission.link_entities(submission_entity, entity)

    def __add_errors(self, submission: Submission, response: Element):
        submission_errors = []
        for messages in response.iter('MESSAGES'):
            for error in messages.iter('ERROR'):
                match = self.regex.match(error.text)
                if match:
                    self.__add_error(submission, match)
                else:
                    submission_errors.append(error.text)
        if submission_errors:
            raise EnaError(' '.join(submission_errors))

    def __add_error(self, submission: Submission, match: Match):
        ena_name = match.group('name').upper()
        alias = match.group('alias')
        if ena_name in self.map:
            entity_type, accession_type = self.map[ena_name]
            entity = submission.get_entity(entity_type, alias)
            entity.add_error(
                f'{entity_type}_{accession_type}_accession'.lower(),
                match.group('message')
            )
