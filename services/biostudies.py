import uuid
from typing import List

from biostudiesclient.api import Api
from biostudiesclient.auth import Auth

from submission_broker.submission.entity import Entity
from submission_broker.submission.submission import Submission

BIOSTUDIES_LINK_TYPES = {
    'sample': 'biosample',
    'study': 'ena',
    'run_experiment': 'ena'
}

ENTITY_TYPE_SERVICE = {
    'sample': 'BioSamples',
    'run_experiment': 'ENA_Run'
}


class BioStudies:
    def __init__(self, base_url=None, username=None, password=None):
        self.base_url = base_url
        self.auth = Auth(base_url)

        self.session_id = self.__get_session_id(username, password)
        self.api = Api(self.auth)
        self.submission_folder_name = uuid.uuid1()

    def create_submission_folder(self):
        return self.api.create_user_sub_folder(self.submission_folder_name)

    def upload_file(self, file_path):
        return self.api.upload_file(
            file_path,
            self.submission_folder_name)

    def send_submission(self, submission: dict):
        files = self.__get_files_info(submission)
        if len(files) > 0:
            self.__process_files(files)

        response = self.api.create_submission(submission)

        return response.json['accno']

    def get_submission_by_accession(self, accession_id):
        return self.api.get_submission(accession_id)

    def update_links_in_submission(self, submission: Submission, study: Entity) -> dict:
        study_accession = study.get_accession('BioStudies')
        biostudies_submission = self.get_submission_by_accession(study_accession).json
        links_section = self.__get_links_section_from_submission(biostudies_submission)
        self.__update_links_section(links_section, study, submission)
        return biostudies_submission

    @staticmethod
    def __get_links_section_from_submission(submission: dict) -> List:
        section = submission['section']
        return section.setdefault('links', [])

    def __update_links_section(self, links_section: List, study: Entity, submission: Submission):
        for entity_type, biostudies_type in BIOSTUDIES_LINK_TYPES.items():
            for linked_entity in submission.get_linked_entities(study, entity_type):
                accession = linked_entity.get_accession(ENTITY_TYPE_SERVICE[entity_type])
                if accession and not self.__accession_in_list(links_section, accession):
                    link_to_add = self.__create_link_element(biostudies_type, accession)
                    links_section.append(link_to_add)

    @staticmethod
    def __create_link_element(link_type, accession):
        return {
            'url': accession,
            'attributes': [
                {
                    'name': 'Type',
                    'value': link_type
                }
            ]
        }

    @staticmethod
    def __accession_in_list(links_section, accession):
        for element in links_section:
            element_accession = element.get('url', None)
            if element_accession and element_accession == accession:
                return True
        return False

    def __get_session_id(self, username, password):
        return self.__get_auth_response(username, password).session_id

    def __get_auth_response(self, username, password):
        return self.auth.login(username, password)

    @staticmethod
    def __get_files_info(submission):
        section = submission["section"]
        return section["files"] if "files" in section else []

    def __process_files(self, files):
        self.create_submission_folder()

        for file in files:
            file_path = file["path"]
            self.upload_file(file_path)

        # TODO: wait while file uploads finished - not needed for COVID-19 template
