import json
import unittest
from os.path import dirname, join

from submission.submission import Entity, Submission


class TestSubmissionErrors(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        with open(join(dirname(__file__), "../../resources/data_for_test_issues.json")) as test_data_file:
            test_data = json.load(test_data_file)
        self.submission = Submission()
        for entity_type, attributes in test_data.items():
            self.submission.map(entity_type, attributes["index"], attributes)

    def test_submission_with_no_errors(self):
        # Given
        study: Entity = self.submission.get_entity('study', 'PRJEB39632')

        # Then
        self.assertFalse(study.has_errors())
        self.assertDictEqual({}, self.submission.get_type_errors('study'))
        self.assertFalse(self.submission.has_errors())
        self.assertDictEqual({}, self.submission.get_all_errors())
    
    def test_submission_entity_with_error(self):
        # Given
        expected_errors = {
            'study': {
                'PRJEB39632': {
                    'release_date': ["should have required property 'release_date'"]
                }
            }
        }
        study: Entity = self.submission.get_entity('study', 'PRJEB39632')

        # When
        study.add_error('release_date', "should have required property 'release_date'")
        
        # Then
        self.assertTrue(study.has_errors())
        self.assertTrue(self.submission.has_errors())
        self.assertDictEqual(expected_errors['study']['PRJEB39632'], study.get_errors())
        self.assertDictEqual(expected_errors['study'], self.submission.get_type_errors('study'))
        self.assertDictEqual(expected_errors, self.submission.get_all_errors())
    
    def test_submission_entities_with_errors(self):
        # Given
        expected_errors = {
            'study': {
                'PRJEB39632': {
                    'email_address': ["should have required property 'email_address'"]
                }
            },
            'isolate_genome_assembly_information': {
                'P17157_1007': {
                    'assembly_type': ["should be equal to one of the allowed values: ['covid-19 outbreak']"],
                    'coverage': ["should have required property 'coverage'"]
                }
            }
        }
        study: Entity = self.submission.get_entity('study', 'PRJEB39632')
        assembly: Entity = self.submission.get_entity('isolate_genome_assembly_information', 'P17157_1007')
        
        # When
        study.add_error('email_address',  "should have required property 'email_address'")
        assembly.add_error('assembly_type', "should be equal to one of the allowed values: ['covid-19 outbreak']")
        assembly.add_error('coverage', "should have required property 'coverage'")
        
        # Then
        self.assertTrue(self.submission.has_errors())
        self.assertDictEqual(expected_errors, self.submission.get_all_errors())


if __name__ == '__main__':
    unittest.main()
