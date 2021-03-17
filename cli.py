import argparse
import json
import logging
import os
import sys
from copy import copy
from contextlib import closing
from datetime import date

from conversion.biosamples import BioSamplesConverter
from conversion.biostudies import BioStudyConverter
from conversion.ena.submission import EnaSubmissionConverter
from conversion.ena.response import EnaResponseConverter
from excel.markup import ExcelMarkup
from excel.validate import ValidatingExcel
from services.biosamples import BioSamples, AapClient
from services.biostudies import BioStudies
from services.ena import EnaAction, Ena
from validation.docker import DockerValidator
from validation.taxonomy import TaxonomyValidator
from validation.upload import UploadValidator
from validation.xsd import XMLSchemaValidator


DOCKER_IMAGE = "dockerhub.ebi.ac.uk/ait/json-schema-validator"
SCHEMA_VALIDATION_URL = "http://localhost:3020/validate"


class CovidExcelUtils:
    def __init__(self, file_path, output):
        self.__file_path = file_path
        self.__output = output
        self.excel = None
        self.ena_files = {}
        self.ena_response = None

    def load(self):
        if 'excel' in self.__output:
            self.excel = ExcelMarkup(self.__file_path)
        else:
            self.excel = ValidatingExcel(self.__file_path)

    def validate(self, secure_key: str = None):
        docker_error = False
        try:
            with closing(DockerValidator(DOCKER_IMAGE, SCHEMA_VALIDATION_URL)) as docker:
                self.excel.validate(docker)
        except Exception:
            logging.warning(f'Error validating using JSON Validator on Docker. Will validate using ENA XML schema instead.')
            docker_error = True
        self.excel.validate(TaxonomyValidator())
        if secure_key:
            self.excel.validate(UploadValidator(secure_key))
        if docker_error:
            self.excel.validate(XMLSchemaValidator())

    def submit_to_biosamples(self, converter: BioSamplesConverter, service: BioSamples):
        for sample in self.excel.data.get_entities('sample'):
            try:
                converted_sample = converter.convert_sample(sample)
                response = service.send_sample(converted_sample)
                if 'accession' in response:
                    sample.add_accession('BioSamples', response['accession'])
            except Exception as e:
                error_msg = f'BioSamples Error: {e}'
                sample.add_error('sample_accession', error_msg)

    def submit_to_biostudies(self, service: BioStudies):
        for study in self.excel.data.get_entities("study"):
            try:
                bio_study_submission = BioStudyConverter.convert_study(study)
                accession = service.send_submission(bio_study_submission)
                study.add_accession('BioStudies', accession)
            except Exception as e:
                error_msg = f'BioStudies Error: {e}'
                study.add_error('study_accession', error_msg)

    def update_biostudies_links(self, service: BioStudies):
        for study in self.excel.data.get_entities('study'):
            biostudies_accession = study.get_accession('BioStudies')
            if biostudies_accession:
                try:
                    biostudies_submission = service.update_links_in_submission(self.excel.data, study)
                    service.send_submission(biostudies_submission)
                except Exception as e:
                    error_msg = f'BioStudies Error: {e}'
                    study.add_error('study_accession', error_msg)

    def submit_ena(self, service: Ena, action: EnaAction = None, hold_date: date = None, center: str = None):
        submission_converter = EnaSubmissionConverter()
        self.ena_files = submission_converter.get_ena_files(self.excel.data)
        if not action:
            action = EnaAction.ADD
            for key in self.excel.data.get_all_accessions().keys():
                if key.startswith('ENA_'):
                    action = EnaAction.MODIFY
                    break
        if not hold_date:
            hold_date = submission_converter.get_release_date(self.excel.data)
        self.ena_response = service.submit_files(self.ena_files, action, hold_date, center)
        EnaResponseConverter().convert_response_file(self.excel.data, self.ena_response)

    def close(self):
        if self.excel:
            if isinstance(self.excel, ExcelMarkup):
                self.excel.add_ena_submission_index()
                self.excel.add_accessions()
                self.excel.markup_with_errors()
                self.excel.close()
                logging.info(f'Excel file updated: {self.__file_path}')
            input_file_name = os.path.splitext(self.__file_path)[0]
            if 'json' in self.__output:
                json_file_path = input_file_name + '.json'
                if self.excel.data.has_data():
                    self.write_dict(json_file_path, self.excel.data.as_dict())
                    logging.info(f'JSON output written to: {json_file_path}')
                if self.excel.data.has_errors():
                    issues_file_path = input_file_name + '_issues.json'
                    self.write_dict(issues_file_path, self.excel.data.get_all_errors())
                    logging.info(f'JSON issues written to: {issues_file_path}')
            if 'ena_xml' in self.__output:
                if self.ena_files:
                    for ena_file_name, xml_bytes in self.ena_files.values():
                        ena_file_path = input_file_name + '_ena_' + ena_file_name
                        self.write_bytes(ena_file_path, xml_bytes)
                        logging.info(f'ENA Submission File written to: {ena_file_path}')
                if self.ena_response:
                    ena_file_path = input_file_name + '_ena_RESPONSE.xml'
                    self.write_bytes(ena_file_path, self.ena_response)
                    logging.info(f'ENA Response File written to: {ena_file_path}')

    @staticmethod
    def write_dict(file_path: str, data: dict):
        file_path = os.path.abspath(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, "w") as open_file:
            json.dump(data, open_file, indent=2)

    @staticmethod
    def write_bytes(file_path: str, data: bytes):
        file_path = os.path.abspath(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, "wb") as open_file:
            open_file.write(data)


def set_logging_level(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)
    logging.basicConfig(level=numeric_level)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse, Validate and Submit excel files to EBI Resources'
    )
    parser.add_argument(
        'file_path', type=str,
        help='path of excel file to load'
    )
    accepted_outputs = ['all', 'excel', 'json', 'ena_xml']
    parser.add_argument(
        '--output', type=str,
        default='excel',
        help=' Comma separated list of outputs, accepts: all,excel,json,ena_xml. "excel" will update validation and submission errors into the passed excel file as notes, styling the cells red. "json" will create a .json of the parsed excel objects annotated with errors with an _issues.json file of errors. "ena_xml" will save the request XML files used to generate the ENA Submission and any received response'
    )
    parser.add_argument(
        '--biosamples', action='store_true',
        help='Submit to BioSamples, requires environment variables AAP_USERNAME and AAP_PASSWORD'
    )
    parser.add_argument(
        '--biosamples_domain', type=str,
        help='Set the default BioSamples domain to use when the domain is not found in the excel file.'
    )
    parser.add_argument(
        '--biosamples_url', type=str, default='https://www.ebi.ac.uk/biosamples',
        help='Override the default URL for BioSamples API: https://www.ebi.ac.uk/biosamples'
    )

    parser.add_argument(
        '--biostudies', action='store_true',
        help='Submit to BioStudies, requires environment variables BIOSTUDIES_USERNAME and BIOSTUDIES_PASSWORD'
    )
    parser.add_argument(
        '--biostudies_url', type=str, default='http://biostudy-bia.ebi.ac.uk:8788',
        help='Override the default URL for BioStudies REST API: http://biostudy-bia.ebi.ac.uk:8788'
    )
    parser.add_argument(
        '--aap_url', type=str, default='https://api.aai.ebi.ac.uk',
        help='Override the default URL for AAP API: https://api.aai.ebi.ac.uk'
    )
    parser.add_argument(
        '--ena', action='store_true',
        help='Submit to ENA, requires environment variables ENA_USERNAME and ENA_PASSWORD'
    )
    parser.add_argument(
        '--ena_url', type=str, default='https://www.ebi.ac.uk/ena',
        help='Override the default URL for ENA REST API and ENA Taxonomy Validator: https://www.ebi.ac.uk/ena'
    )
    parser.add_argument(
        '--ena_action', type=str, choices=['ADD', 'MODIFY', 'VALIDATE', 'VALIDATE,ADD', 'VALIDATE,MODIFY'],
        help='Define an ENA action to use when submitting, default is ADD'
    )
    parser.add_argument(
        '--ena_hold_date', type=date,
        help='Define a Hold Date to use when submitting to ENA, overriding any hold date defined in the excel file.'
    )
    parser.add_argument(
        '--ena_center_name', type=str,
        help='Define a submitting center name to use when submitting to ENA'
    )
    parser.add_argument(
        '--secure_key', type=str,
        help='The secure key used when uploading files to the drag-and-drop data submission tool, if this is present we will validate that all the files are accounted for. Format: xxxxx-xxx-xxxx-xxxxx'
    )
    parser.add_argument(
        '--log_level', '-l', type=str, default='INFO',
        help='Override the default logging level: INFO',
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
    )
    args = vars(parser.parse_args())
    set_logging_level(args['log_level'])
    outputs = args['output'].split(',')
    for out in outputs:
        if out not in accepted_outputs:
            logging.error(f'Unaccepted output parameter detected, "{out}" is not in the list of accepted outputs.')
            sys.exit(2)
    if 'all' in outputs:
        outputs = copy(accepted_outputs)
        outputs.remove('all')
    with closing(CovidExcelUtils(args['file_path'], outputs)) as excel_utils:
        excel_utils.load()
        if not excel_utils.excel.data.has_data:
            logging.info(f"No Data imported from: {args['file_path']}")
            sys.exit(0)
        excel_utils.validate(args['secure_key'])
        if excel_utils.excel.data.has_errors():
            message = 'Issues detected:'
            for entity_type, indexed_entities in excel_utils.excel.data.get_all_errors().items():
                message = f'{message} {len(indexed_entities)} {entity_type}(s)'
            print(message)
            if args['biosamples'] or args['biostudies'] or args['ena']:
                user_text = input('Continue with Brokering? (y/N)?:')
                if not user_text.lower().startswith('y'):
                    print('Exiting')
                    sys.exit(0)

        biosamples_service = None
        biosamples_accessions = []
        if args['biosamples']:
            if 'AAP_USERNAME' not in os.environ:
                logging.error('No AAP_USERNAME detected in os environment variables.')
                sys.exit(2)
            if 'AAP_PASSWORD' not in os.environ:
                logging.error('No AAP_PASSWORD detected in os environment variables.')
                sys.exit(2)
            logging.info(f"Attempting to Submit to BioSamples: {args['biosamples_url']}, AAP: {args['aap_url']}")
            try:
                aap_client = AapClient(url=args['aap_url'], username=os.environ['AAP_USERNAME'], password=os.environ['AAP_PASSWORD'])
                biosamples_service = BioSamples(aap_client, args['biosamples_url'])
                biosamples_converter = BioSamplesConverter(excel_utils.excel.column_map, args['biosamples_domain'])
                excel_utils.submit_to_biosamples(biosamples_converter, biosamples_service)
            except Exception as error:
                logging.error(f'BioSamples Error: {error}')
                sys.exit(2)

        biostudies_service = None
        biostudies_accessions = []
        if args['biostudies']:
            if 'BIOSTUDIES_USERNAME' not in os.environ:
                logging.error('No BIOSTUDIES_USERNAME detected in os environment variables.')
                sys.exit(2)
            if 'BIOSTUDIES_PASSWORD' not in os.environ:
                logging.error('No BIOSTUDIES_PASSWORD detected in os environment variables.')
                sys.exit(2)
            logging.info(f"Attempting to Submit to BioStudies: {args['biostudies_url']}")
            try:
                biostudies_service = BioStudies(args['biostudies_url'], os.environ['BIOSTUDIES_USERNAME'], os.environ['BIOSTUDIES_PASSWORD'])
                excel_utils.submit_to_biostudies(biostudies_service)
            except Exception as error:
                logging.error(f'BioStudies Error: {error}')
                sys.exit(2)
        
        if args['ena']:
            if 'ENA_USERNAME' not in os.environ:
                logging.error('No ENA_USERNAME detected in os environment variables.')
                sys.exit(2)
            if 'ENA_PASSWORD' not in os.environ:
                logging.error('No ENA_PASSWORD detected in os environment variables.')
                sys.exit(2)
            ena_action = None
            if args['ena_action']:
                ena_action = EnaAction(args['ena_action'])
            try:
                ena_service = Ena(os.environ['ENA_USERNAME'], os.environ['ENA_PASSWORD'], args['ena_url'])
                excel_utils.submit_ena(ena_service, ena_action, args['ena_hold_date'], args['ena_center_name'])
            except Exception as error:
                logging.error(f'ENA Error: {error}')
                sys.exit(2)

        if biostudies_service:
            excel_utils.update_biostudies_links(biostudies_service)
