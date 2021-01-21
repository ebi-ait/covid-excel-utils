import argparse
import json
import logging
import os
import sys
from contextlib import closing

from lxml import etree
from xml.etree.ElementTree import Element
from services.biosamples import AapClient, BioSamples
from excel.markup import ExcelMarkup
from excel.validate import ValidatingExcel
from conversion.ena.submission import EnaSubmissionConverter
from validation.docker import DockerValidator
from validation.excel import ExcelValidator
from validation.taxonomy import TaxonomyValidator


class CovidExcelUtils:
    docker_image = "dockerhub.ebi.ac.uk/ait/json-schema-validator"
    validation_url = "http://localhost:3020/validate"
    ena_url = 'https://www.ebi.ac.uk/ena'
    excel = None

    def __init__(self, file_path, output):
        self.__file_path = file_path
        self.__output = output
        self.__ena_converter = EnaSubmissionConverter()
        self.ena_submission = None

    def load(self):
        if self.__output in ['all', 'excel']:
            self.excel = ExcelMarkup(self.__file_path)
        else:
            self.excel = ValidatingExcel(self.__file_path)

    def validate(self):
        try:
            with closing(DockerValidator(self.docker_image, self.validation_url)) as validator:
                self.excel.validate(validator)
        except Exception as error:
            logging.warning(f'Error validating schema, using best guess validation. Detected Error: {error}')
            self.excel.validate(ExcelValidator(self.__file_path))
        self.excel.validate(TaxonomyValidator(self.ena_url))

    def submit_biosamples(self, url, domain, aap_url, aap_username, aap_password):
        logging.info(f'Attempting to Submit to BioSamples: {url}, AAP: {aap_url}')
        aap_client = AapClient(url=aap_url, username=aap_username, password=aap_password)
        biosamples = BioSamples(aap_client, url, domain)
        biosamples_count = 0
        for row in self.excel.data.values():
            if 'sample' in row:
                sample = row['sample']
                try:
                    sample['request'] = biosamples.encode_sample(sample)
                    sample['biosample'] = biosamples.send_sample(sample['request'])
                    sample.pop('request')
                    if 'accession' in sample['biosample']:
                        sample['study_accession'] = sample['biosample']['accession']
                    biosamples_count = biosamples_count + 1
                except Exception as error:
                    error_msg = f'Encoding Error: {error}'
                    row['sample'].setdefault('errors', {}).setdefault('sample_accession', []).append(error_msg)
        logging.info(f'Successfully submitted {biosamples_count} BioSamples')
    
    def submit_ena(self):
        self.ena_submission = self.__ena_converter.convert(self.excel.data)

    def close(self):
        if self.excel:
            if isinstance(self.excel, ExcelMarkup):
                self.excel.add_biosample_accessions()
                self.excel.markup_with_errors()
                self.excel.close()
                logging.info(f'Excel file updated: {self.__file_path}')
            if self.__output in ['all', 'json']:
                input_file_name = os.path.splitext(self.__file_path)[0]
                if self.excel.data:
                    json_file_path = input_file_name + '.json'
                    self.write_dict(json_file_path, self.excel.data)
                    logging.info(f'JSON output written to: {json_file_path}')
                # ToDo: Remove this? USeful for debugging 
                if self.ena_submission:
                    for ena_file_name, xml_element in self.ena_submission.files().items():
                        ena_file_path = input_file_name + '_ena_' + ena_file_name
                        self.write_xml(ena_file_path, xml_element)
                        logging.info(f'ENA Submission File written to: {ena_file_path}')  
                if self.excel.errors:
                    issues_file_path = input_file_name + '_issues.json'
                    self.write_dict(issues_file_path, self.excel.human_errors())
                    logging.info(f'JSON issues written to: {issues_file_path}')

    @staticmethod
    def write_dict(file_path: str, data: dict):
        file_path = os.path.abspath(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, "w") as open_file:
            json.dump(data, open_file, indent=2)
    
    @staticmethod
    def write_xml(file_path: str, xml_element: Element):
        file_path = os.path.abspath(file_path)
        xml_bytes = etree.tostring(xml_element, xml_declaration=True, pretty_print=True, encoding="UTF-8")
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, "wb") as open_file:
            open_file.write(xml_bytes)


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
    parser.add_argument(
        '--output', type=str,
        choices=['all', 'excel', 'json'],
        default='excel',
        help='Override the default output of "excel" which will update validation and submission errors into the passed excel file as notes, styling the cells red. "json" will create a .json of the parsed excel objects annotated with errors with an _issues.json file of errors by row. "all" will do both.'
    )
    parser.add_argument(
        '--biosamples', action='store_true',
        help='Submit to BioSamples, requires environment variables AAP_USERNAME and AAP_PASSWORD'
    )
    parser.add_argument(
        '--biosamples_domain', type=str,
        help='Override the BioSamples domain rather than detect the domain from the excel file.'
    )
    parser.add_argument(
        '--biosamples_url', type=str, default='https://www.ebi.ac.uk/biosamples',
        help='Override the default URL for BioSamples API: https://www.ebi.ac.uk/biosamples'
    )
    parser.add_argument(
        '--aap_url', type=str, default='https://api.aai.ebi.ac.uk',
        help='Override the default URL for AAP API: https://api.aai.ebi.ac.uk'
    )
    parser.add_argument(
        '--ena', action='store_true',
        help='Submit to ENA'
    )
    parser.add_argument(
        '--log_level', '-l', type=str, default='INFO',
        help='Override the default logging level: INFO',
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
    )
    args = vars(parser.parse_args())
    set_logging_level(args['log_level'])
    with closing(CovidExcelUtils(args['file_path'], args['output'])) as excel_utils:
        excel_utils.load()
        if not excel_utils.excel.data:
            logging.info(f"No Data imported from: {args['file_path']}")
            sys.exit(0)
        excel_utils.validate()
        if args['biosamples']:
            if excel_utils.excel.errors:
                user_text = input(f'Issues from {len(excel_utils.excel.errors)} rows detected. Continue with BioSamples Submission? (y/N)?:')
                if not user_text.lower().startswith('y'):
                    print('Exiting')
                    sys.exit(0)
            if 'AAP_USERNAME' not in os.environ:
                logging.error('No AAP_USERNAME detected in os environment variables.')
                sys.exit(2)
            if 'AAP_PASSWORD' not in os.environ:
                logging.error('No AAP_PASSWORD detected in os environment variables.')
                sys.exit(2)
            excel_utils.submit_biosamples(
                args['biosamples_url'],
                args['biosamples_domain'],
                args['aap_url'],
                os.environ['AAP_USERNAME'],
                os.environ['AAP_PASSWORD']
            )
        if args['ena']:
            excel_utils.submit_ena()
