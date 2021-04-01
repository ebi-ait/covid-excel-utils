import unittest
from http import HTTPStatus
from biostudiesclient.auth import Auth, AuthResponse
from biostudiesclient.exceptions import RestErrorException

from unittest.mock import MagicMock

from biostudiesclient.response_utils import ResponseObject
from submission_broker.submission.entity import Entity, EntityIdentifier
from submission_broker.submission.submission import Submission

from services.biostudies import BioStudies


class TestBioStudiesService(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.mock_auth = Auth

    def test_given_credentials_can_get_session_id(self):
        test_session_id = "test.session.id"

        auth_response = AuthResponse(status=HTTPStatus(200))
        auth_response.session_id = test_session_id

        self.mock_auth.login = MagicMock(return_value=auth_response)

        biostudies = BioStudies("url", "username", "password")

        session_id = biostudies.session_id

        self.assertEqual(session_id, test_session_id)

    def test_given_incorrect_credentials_raise_exception(self):
        auth_error_message = "Invalid email address or password."

        status_code_unauthorised = 401
        self.mock_auth.login = MagicMock(side_effect=RestErrorException(auth_error_message, status_code_unauthorised))

        with self.assertRaises(RestErrorException) as context:
            BioStudies("url", "bad_username", "bad_password")

        self.assertTrue(auth_error_message in context.exception.message)
        self.assertEqual(HTTPStatus.UNAUTHORIZED, context.exception.status_code)

    def test_create_sub_folder_returns_success(self):
        pass  # TODO

    def test_upload_file_returns_success(self):
        pass  # TODO

    def test_given_valid_submission_payload_response_with_accession(self):
        test_session_id = "test.session.id"

        auth_response = AuthResponse(status=HTTPStatus(200))
        auth_response.session_id = test_session_id

        self.mock_auth.login = MagicMock(return_value=auth_response)

        bst_accession_id = 'bst123'

        response = ResponseObject()
        response.json = {'accno': bst_accession_id}

        biostudies = BioStudies("url", "username", "password")
        biostudies.api.create_submission = MagicMock(return_value=response)

        accession_from_response = biostudies.send_submission(TestBioStudiesService.__create_submission())

        self.assertEqual(bst_accession_id, accession_from_response)

    def test_given_valid_submission_payload_with_files_response_with_accession(self):
        test_session_id = "test.session.id"

        auth_response = AuthResponse(status=HTTPStatus(200))
        auth_response.session_id = test_session_id

        self.mock_auth.login = MagicMock(return_value=auth_response)

        bst_accession_id = 'bst124'
        response = ResponseObject()
        response.json = {'accno': bst_accession_id}

        biostudies = BioStudies("url", "username", "password")
        biostudies.api.create_submission = MagicMock(return_value=response)
        biostudies.api.create_user_sub_folder = MagicMock()
        biostudies.api.upload_file = MagicMock()

        accession_from_response = biostudies.send_submission(TestBioStudiesService.__create_submission_with_files())

        self.assertEqual(bst_accession_id, accession_from_response)

    def test_given_invalid_submission_payload_response_with_error(self):
        test_session_id = "test.session.id"

        auth_response = AuthResponse(status=HTTPStatus(200))
        auth_response.session_id = test_session_id

        self.mock_auth.login = MagicMock(return_value=auth_response)

        biostudies = BioStudies("url", "username", "password")
        expected_error_message = "Submission validation errors."
        biostudies.api.create_submission = MagicMock(
            side_effect=RestErrorException(expected_error_message, HTTPStatus.BAD_REQUEST))

        with self.assertRaises(RestErrorException) as context:
            biostudies.send_submission(TestBioStudiesService.__create_submission())

        self.assertEqual(HTTPStatus.BAD_REQUEST, context.exception.status_code)
        self.assertEqual(expected_error_message, context.exception.message)

    def test_when_study_contains_new_links_then_those_added_to_submission(self):
        # Given
        test_session_id = "test.session.id"
        auth_response = AuthResponse(status=HTTPStatus(200))
        auth_response.session_id = test_session_id
        self.mock_auth.login = MagicMock(return_value=auth_response)
        biostudies = BioStudies("url", "username", "password")

        response = ResponseObject()
        response.json = self.__create_submission()
        biostudies.get_submission_by_accession = MagicMock(return_value=response)

        submission = Submission()
        study = submission.map('study', 'test alias', attributes={})
        study.add_accession('test', 'PRJ1234')
        self.__link_entity_accessions(submission, study)
        expected_links = [
            {'url': 'ABC1234', 'attributes': [{'name': 'Type', 'value': 'ena'}]},
            {'url': 'SAME123', 'attributes': [{'name': 'Type', 'value': 'biosample'}]},
            {'url': 'SAME456', 'attributes': [{'name': 'Type', 'value': 'biosample'}]},
            {'url': 'SAME789', 'attributes': [{'name': 'Type', 'value': 'biosample'}]}
        ]

        # When
        biostudies_submission = biostudies.update_links_in_submission(submission, study)

        # Then
        links_section = biostudies_submission.get('section', {}).get('links', [])
        self.assertTrue(links_section)
        for expected_element in expected_links:
            self.assertIn(expected_element, links_section)
        self.assertCountEqual(expected_links, links_section)

    @staticmethod
    def __create_submission():
        return {
            'attributes': [
                {
                    'name': 'Name',
                    'value': 'Test submission'
                }
            ],
            'section': {
                'type': 'Study',
                'attributes': [
                    {
                        'name': 'Title',
                        'value': 'Test title'
                    }
                ],
                'links': [
                    {
                        'url': 'ABC1234',
                        'attributes': [
                            {
                                'name': 'Type',
                                'value': 'ena'
                            }
                        ]
                    }
                ],
                'subsections': [
                    {
                        'type': 'Author',
                        'attributes': [
                            {
                                'name': 'email',
                                'value': 'joe@example.com'
                            }
                        ]
                    }
                ]
            }
        }

    @staticmethod
    def __create_submission_with_files():
        submission = TestBioStudiesService.__create_submission()
        submission['section']['files'] = [
            {
                'path': 'resources/valid_study.json',
                'attributes': [
                    {
                        'name': 'Description',
                        'value': 'Raw test data file'
                    }
                ]
            }
        ]

        return submission

    @staticmethod
    def __link_entity_accessions(submission: Submission, entity: Entity):
        run = submission.map('experiment_run', 'ABC1234', {})
        run.add_accession('ENA', 'ABC1234')
        for index in [123, 456, 789]:
            new_entity = submission.map('sample', str(index), {})
            new_entity.add_accession('BioSamples', f'SAME{index}')
            entity.add_link('sample', new_entity.identifier.index)

    @staticmethod
    def __create_entity_identifier(entity_type, index):
        return EntityIdentifier(entity_type, index)


if __name__ == '__main__':
    unittest.main()
