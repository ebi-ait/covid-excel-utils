import uuid

from biostudiesclient.api import Api
from biostudiesclient.auth import Auth

from submission.entity import Entity

LINK_TYPE_MAP = {
    'sample': 'BioSamples',
    'study': 'ENA',
    'run_experiment': 'ENA'
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

    def update_links_in_submission(self, submission: dict, study: Entity):
        links_section = self.__get_links_section_from_submission(submission)

        self.__update_links_section(links_section, study)

    @staticmethod
    def __get_links_section_from_submission(submission) -> dict:
        section = submission['section']
        return section.setdefault('links', [])

    def __update_links_section(self, links_section, study: Entity):
        for entity_type, entity_ids in study.links.items():
            if entity_type not in LINK_TYPE_MAP:
                continue
            link_type = LINK_TYPE_MAP[entity_type]

            for entity_id in entity_ids:

                other_object_accession_id = entity_id.accession

                if other_object_accession_id:
                    link_to_add = self.__create_link_element(link_type, other_object_accession_id)
                    links_section.append(link_to_add)

    @staticmethod
    def __create_link_element(link_type, other_object_accession_id):
        return {
            'url': other_object_accession_id,
            'attributes': [
                {
                    'name': 'Type',
                    'value': link_type
                }
            ]
        }

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
