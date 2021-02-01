import unittest
from http import HTTPStatus

from biostudiesclient.auth import Auth, AuthResponse
from biostudiesclient.exceptions import RestErrorException

from unittest.mock import MagicMock

from services.biostudies import BioStudies


class TestBioStudiesServiceAuth(unittest.TestCase):

    def test_given_credentials_can_get_session_id(self):
        test_session_id = "test.session.id"

        auth_response = AuthResponse(status=HTTPStatus(200))
        auth_response.session_id = test_session_id
        mock_auth = Auth

        mock_auth.login = MagicMock(return_value=auth_response)

        biostudies = BioStudies("url", "username", "password")

        session_id = biostudies.session_id

        self.assertEqual(session_id, test_session_id)

    def test_given_incorrect_credentials_raise_exception(self):
        auth_error_message = "Invalid email address or password."

        mock_auth = Auth
        status_code_unauthorised = 401
        mock_auth.login = MagicMock(side_effect=RestErrorException(auth_error_message, status_code_unauthorised))

        with self.assertRaises(RestErrorException) as context:
            BioStudies("url", "bad_username", "bad_password")

        self.assertTrue(auth_error_message in context.exception.message)
        self.assertEqual(HTTPStatus.UNAUTHORIZED, context.exception.status_code)


if __name__ == '__main__':
    unittest.main()
