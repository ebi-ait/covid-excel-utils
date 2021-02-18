import argparse
import json
import logging
import os
import sys
from contextlib import closing

from lxml import etree
from xml.etree.ElementTree import Element

from conversion.biostudies.bio_study_converter import BioStudyConverter
from excel.markup import ExcelMarkup
from excel.validate import ValidatingExcel
from conversion.ena.submission import EnaSubmissionConverter
from services.biosamples import BioSamples, AapClient
from services.biostudies import BioStudies
from submission.entity import Entity
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
        self.ena_submission_files = {}

        self.bio_studies_service = BioStudies(
            args['biostudies_url'],
            os.environ['BIOSTUDIES_USERNAME'],
            os.environ['BIOSTUDIES_PASSWORD']
        )

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
        sample: Entity
        for sample in self.excel.data.get_entities('sample'):
            try:
                sample.attributes['request'] = biosamples.encode_sample(sample.attributes)
                sample.attributes['biosample'] = biosamples.send_sample(sample.attributes['request'])
                del sample.attributes['request']
                if 'accession' in sample.attributes['biosample']:
                    # ToDo: introduce accession handling methods to submission class.
                    sample.identifier.accession = sample.attributes['biosample']['accession']
                    sample.attributes['sample_accession'] = sample.identifier.accession
                biosamples_count = biosamples_count + 1
            except Exception as error:
                error_msg = f'BioSamples Error: {error}'
                sample.add_error('sample_accession', error_msg)
        logging.info(f'Successfully submitted {biosamples_count} BioSamples')

    def submit_to_biostudies(self, url):
        logging.info(f'Attempting to Submit to BioStudies: {url}')

        accessions = []
        for bio_study in self.excel.data.get_entities("study"):
            bio_study_submission = BioStudyConverter.convert_study(bio_study)
            accession = self.bio_studies_service.send_submission(bio_study_submission)
            accessions.append(accession)
            bio_study.attributes['bio_study_accession'] = accession

        biostudies_accession_count = len(accessions)
        if biostudies_accession_count > 0:
            logging.info(f'Number of successfully submitted study to BioStudies archive: {biostudies_accession_count}')
            logging.info(f'Accession IDs from BioStudies archive\'s response: {accessions}')

        return accessions

    def update_biostudies_submissions_with_links(self, url):
        logging.info(f'Attempting to update entity links in BioStudies: {url}')

        for study in excel_utils.excel.data.get_entities('study'):
            bio_study_accession = study.attributes['bio_study_accession']

            if bio_study_accession in bio_study_accessions:
                submission = self.bio_studies_service.get_submission_by_accession(bio_study_accession).json
                self.bio_studies_service.update_links_in_submission(submission, study)
                self.bio_studies_service.send_submission(submission)

    def submit_ena(self):
        self.ena_submission_files = EnaSubmissionConverter().convert(self.excel.data)

    def close(self):
        if self.excel:
            if isinstance(self.excel, ExcelMarkup):
                self.excel.add_biosample_accessions()
                self.excel.markup_with_errors()
                self.excel.close()
                logging.info(f'Excel file updated: {self.__file_path}')
            if self.__output in ['all', 'json']:
                input_file_name = os.path.splitext(self.__file_path)[0]
                if self.excel.data.has_data():
                    json_file_path = input_file_name + '.json'
                    self.write_dict(json_file_path, self.excel.data.get_all_data())
                    logging.info(f'JSON output written to: {json_file_path}')
                # ToDo: Remove this when no longer useful for debugging
                if self.ena_submission_files:
                    curl = 'curl -u username:password'
                    for ena_file_name, xml_element in self.ena_submission_files.items():
                        ena_file_path = input_file_name + '_ena_' + ena_file_name + '.xml'
                        self.write_xml(ena_file_path, xml_element)
                        curl = curl + f' -F {ena_file_name}={ena_file_path}'
                        logging.info(f'ENA Submission File written to: {ena_file_path}')  
                    curl = curl + ' "https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/"'
                    print(curl)
                if self.excel.data.has_errors():
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
        if not excel_utils.excel.data.has_data:
            logging.info(f"No Data imported from: {args['file_path']}")
            sys.exit(0)
        excel_utils.validate()
        if args['biosamples']:
            if excel_utils.excel.data.has_errors():
                user_text = input(f'Issues detected. Continue with BioSamples Submission? (y/N)?:')
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

        if args['biostudies']:
            if 'BIOSTUDIES_USERNAME' not in os.environ:
                logging.error('No BIOSTUDIES_USERNAME detected in os environment variables.')
                sys.exit(2)
            if 'BIOSTUDIES_PASSWORD' not in os.environ:
                logging.error('No BIOSTUDIES_PASSWORD detected in os environment variables.')
                sys.exit(2)
            bio_study_accessions = excel_utils.submit_to_biostudies(args['biosamples_url'])

        if args['ena']:
            excel_utils.submit_ena()

        # update archived entities with links
        if args['biostudies']:
            excel_utils.update_biostudies_submissions_with_links(args['biostudies_url'])
