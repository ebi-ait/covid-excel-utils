from biostudiesclient.api import Api
from biostudiesclient.auth import Auth


class BioStudies:

    def __init__(self, base_url=None, username=None, password=None):
        self.base_url = base_url
        self.auth = Auth(base_url)

        self.session_id = self.__get_session_id(username, password)
        self.api = Api(self.auth)

    def __get_session_id(self, username, password):
        return self.__get_auth_response(username, password).session_id

    def __get_auth_response(self, username, password):
        return self.auth.login(username, password)

    def send_submission(self, submission):
        response = self.api.create_submission(submission)

        return response['accno']
