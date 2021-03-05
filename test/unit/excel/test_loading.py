import unittest

from excel.load import ExcelLoader
from excel.submission import ExcelSubmission


class TestExcelLoading(unittest.TestCase):
    def test_loading_accession_equality(self):
        submission = ExcelSubmission()
        study_entity1 = ExcelLoader.map_row_entity(submission, 1, 'study', {'study_accession': 'STUD1'})
        sample_entity1 = ExcelLoader.map_row_entity(submission, 1, 'sample', {'sample_accession': 'SAME1'})

        study_entity2 = ExcelLoader.map_row_entity(submission, 2, 'study', {'study_accession': 'STUD1'})
        sample_entity2 = ExcelLoader.map_row_entity(submission, 2, 'sample', {'sample_accession': 'SAME2'})

        self.assertEqual(study_entity1, study_entity2)
        self.assertNotEqual(sample_entity1, sample_entity2)

    def test_loading_index_equality(self):
        submission = ExcelSubmission()
        study_entity1 = ExcelLoader.map_row_entity(submission, 1, 'study', {'study_alias': 'STUD1'})
        sample_entity1 = ExcelLoader.map_row_entity(submission, 1, 'sample', {'sample_index': 'SAME1'})
        run_entity1 = ExcelLoader.map_row_entity(submission, 1, 'run', {'run_name': 'John'})

        study_entity2 = ExcelLoader.map_row_entity(submission, 2, 'study', {'study_alias': 'STUD1'})
        sample_entity2 = ExcelLoader.map_row_entity(submission, 2, 'sample', {'sample_index': 'SAME1'})
        run_entity2 = ExcelLoader.map_row_entity(submission, 2, 'run', {'run_name': 'Jill'})

        self.assertEqual(study_entity1, study_entity2)
        self.assertEqual(sample_entity1, sample_entity2)
        self.assertNotEqual(run_entity1, run_entity2)
    
    def test_loading_without_index(self):
        submission = ExcelSubmission()
        entity1 = ExcelLoader.map_row_entity(submission, 1, 'lorem', {})
        entity2 = ExcelLoader.map_row_entity(submission, 2, 'ipsum', {})

        self.assertNotEqual(entity1, entity2)
        self.assertEqual('lorem:1', entity1.identifier.index)
        self.assertEqual('ipsum:2', entity2.identifier.index)
    
    def test_links(self):
        submission = ExcelSubmission()
        study_entity1 = ExcelLoader.map_row_entity(submission, 1, 'study', {'study_accession': 'STUD1'})
        sample_entity1 = ExcelLoader.map_row_entity(submission, 1, 'sample', {'sample_accession': 'SAME1'})
        run_entity1 = ExcelLoader.map_row_entity(submission, 1, 'run_experiment', {'run_experiment_accession': 'RUN1'})
        ExcelLoader.map_row_entity(submission, 2, 'study', {'study_accession': 'STUD1'})
        ExcelLoader.map_row_entity(submission, 2, 'sample', {'sample_accession': 'SAME1'})
        run_entity2 = ExcelLoader.map_row_entity(submission, 2, 'run_experiment', {'run_experiment_accession': 'RUN2'})
        
        self.assertSetEqual({'SAME1'}, study_entity1.get_linked_indexes('sample'))
        self.assertSetEqual({'RUN1', 'RUN2'}, study_entity1.get_linked_indexes('run_experiment'))

        self.assertSetEqual({'STUD1'}, sample_entity1.get_linked_indexes('study'))
        self.assertSetEqual({'RUN1', 'RUN2'}, sample_entity1.get_linked_indexes('run_experiment'))

        self.assertSetEqual({'STUD1'}, run_entity1.get_linked_indexes('study'))
        self.assertSetEqual({'SAME1'}, run_entity1.get_linked_indexes('sample'))

        self.assertSetEqual({'STUD1'}, run_entity2.get_linked_indexes('study'))
        self.assertSetEqual({'SAME1'}, run_entity2.get_linked_indexes('sample'))

    def test_loading_differing_index_equality(self):
        # Note: I'm not sure if this is a feature or a bug so if this test fails it's okay,
        # but it's a situation worth noting about our current implementation
        s_1 = {
            's_alias': 'STUD',
            's_index': 'over-written index1',
            's_name': 'over-written name1'
        }
        s_2 = {
            's_index': 'STUD',
            's_name': 'over-written name2'
        }
        s_3 = {
            's_name': 'STUD'
        }
        expected_s = {
            's_alias': 'STUD',
            's_index': 'STUD',
            's_name': 'STUD'
        }
        submission = ExcelSubmission()
        s_entity1 = ExcelLoader.map_row_entity(submission, 1, 's', s_1)
        s_entity2 = ExcelLoader.map_row_entity(submission, 2, 's', s_2)
        s_entity3 = ExcelLoader.map_row_entity(submission, 3, 's', s_3)

        self.assertEqual(s_entity1, s_entity2)
        self.assertEqual(s_entity1, s_entity3)        
        self.assertDictEqual(expected_s, s_entity1.attributes)
