import uuid

from biostudiesclient.api import Api
from biostudiesclient.auth import Auth


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

    def send_submission(self, submission):
        files = self.__get_files_info(submission)
        if len(files) > 0:
            self.__process_files(files)

        response = self.api.create_submission(submission)

        return response.json['accno']

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
