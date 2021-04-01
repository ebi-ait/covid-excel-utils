import unittest
from submission_broker.submission.submission import Submission, HandleCollision


class TestSubmissionMapping(unittest.TestCase):
    def test_mapping_identical_index_update_should_return_same_entity(self):
        submission = Submission(HandleCollision.UPDATE)
        entity_type = "test_case"
        index = "index1"
        entity1 = submission.map(entity_type, index, {})
        entity2 = submission.map(entity_type, index, {})
        self.assertEqual(entity1, entity2)

    def test_mapping_identical_index_overwrite_should_return_same_entity(self):
        submission = Submission(HandleCollision.OVERWRITE)
        entity_type = "test_case"
        index = "index1"
        entity1 = submission.map(entity_type, index, {})
        entity2 = submission.map(entity_type, index, {})
        self.assertEqual(entity1, entity2)

    def test_mapping_identical_index_should_update_entity_attributes(self):
        submission = Submission(HandleCollision.UPDATE)
        entity_type = "test_case"
        index = "index1"
        attributes1 = {
            'first_entity': 'old',
            'both_entities': 'old'
        }
        attributes2 = {
            'second_entity': 'new',
            'both_entities': 'new'
        }
        expected_attributes = {
            'first_entity': 'old',
            'second_entity': 'new',
            'both_entities': 'new'
        }
        entity1 = submission.map(entity_type, index, attributes1)
        entity2 = submission.map(entity_type, index, attributes2)
        self.assertDictEqual(expected_attributes, entity1.attributes)
        self.assertDictEqual(expected_attributes, entity2.attributes)

    def test_mapping_identical_index_should_overwrite_entity_attributes(self):
        submission = Submission(HandleCollision.OVERWRITE)
        entity_type = "test_case"
        index = "index1"
        expected_attributes = {
            'second_entity': 'new'
        }
        entity1 = submission.map(entity_type, index, {'first_entity': 'old'})
        entity2 = submission.map(entity_type, index, {'second_entity': 'new'})
        self.assertDictEqual(expected_attributes, entity1.attributes)
        self.assertDictEqual(expected_attributes, entity2.attributes)        
    
    def test_mapping_identical_index_should_error(self):
        submission = Submission(HandleCollision.ERROR)
        entity_type = "test_case"
        index = "index1"
        submission.map(entity_type, index, {})
        with self.assertRaises(IndexError):
            submission.map(entity_type, index, {})

    def test_has_data_should_start_false(self):
        submission = Submission()
        self.assertFalse(submission.has_data())

    def test_has_data_should_become_true(self):
        submission = Submission()
        submission.map('type', 'index', {})
        self.assertTrue(submission.has_data())
