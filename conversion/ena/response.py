import re
from re import Match
from io import BytesIO
from xml.etree.ElementTree import Element

from lxml import etree

from excel.submission import ExcelSubmission
from submission.entity import Entity
from submission.submission import Submission


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

    def __add_accessions(self, submission: Submission, response: Element):
        for ena_name, entity_type, accession_type in self.map.items():
            for ena_entity in response.iter(ena_name):
                if 'alias' in ena_entity.attrib and 'accession' in ena_entity.attrib:
                    entity = submission.get_entity(entity_type, ena_entity.attrib['alias'])
                    entity.add_accession(accession_type, ena_entity.attrib['accession'])

    def __add_errors(self, submission: Submission, response: Element):
        for messages in response.iter('MESSAGES'):
            for error in messages.iter('ERROR'):
                match = self.regex.match(error.text)
                if match:
                    self.__add_error(submission, match)

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
