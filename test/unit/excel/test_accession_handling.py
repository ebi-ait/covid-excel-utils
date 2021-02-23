import unittest

from excel.load import ExcelLoader
from excel.submission import ExcelSubmission


class TestExcelAccessionHandling(unittest.TestCase):
    def test_adding_mapped_or_default_service_accessions(self):
        expected_accessions = {
            'BioStudies': ['PRJEB12345'],
            'BioSamples': ['SAME123'],
            'ENA': ['EXP123', 'EXP456']
        }
        submission = ExcelSubmission()
        study = {
            'study_accession': 'PRJEB12345'
        }
        sample = {
            'sample_accession': 'SAME123'
        }
        run_experiment1 = {
            'run_experiment_accession': 'EXP123',
        }
        run_experiment2 = {
            'run_experiment_ena_accession': 'EXP456',
        }
        study_entity1 = ExcelLoader.map_row_entity(submission, 1, 'study', study)
        sample_entity1 = ExcelLoader.map_row_entity(submission, 1, 'sample', sample)
        run_entity1 = ExcelLoader.map_row_entity(submission, 1, 'run_experiment', run_experiment1)

        study_entity2 = ExcelLoader.map_row_entity(submission, 2, 'study', study)
        sample_entity2 = ExcelLoader.map_row_entity(submission, 2, 'sample', sample)
        run_entity2 = ExcelLoader.map_row_entity(submission, 2, 'run_experiment', run_experiment2)

        self.assertEqual(study_entity1, study_entity2)
        self.assertEqual(sample_entity1, sample_entity2)
        self.assertNotEqual(run_entity1, run_entity2)
        
        self.assertDictEqual(expected_accessions, submission.get_all_accessions())
        self.assertEqual('PRJEB12345', study_entity1.identifier.index)
        self.assertEqual('PRJEB12345', study_entity1.get_accession('BioStudies'))

        self.assertEqual('SAME123', sample_entity1.identifier.index)
        self.assertEqual('SAME123', sample_entity1.get_accession('BioSamples'))

        self.assertEqual('EXP123', run_entity1.identifier.index)
        self.assertEqual('EXP123', run_entity1.get_accession('ENA'))

        # only accessions in the format {entity_type}_accession can be used for indexes
        self.assertEqual('run_experiment:2', run_entity2.identifier.index)
        self.assertEqual('EXP456', run_entity2.get_accession('ENA'))
    
    def test_unmapped_service_accessions(self):
        expected_accessions = {
            'BioSamples': ['SAME123'],
            'BioStudies': ['PRJEB12345'],
            'ENA': ['ENA-PROJECT-1', 'ENA-SAMPLE-1', 'EXP123', 'EXP456'],
            'eva': ['EVA1', 'EVA2']
        }
        submission = ExcelSubmission()
        study = {
            'study_accession': 'PRJEB12345',
            'study_ena_accession': 'ENA-PROJECT-1'
        }
        sample = {
            'sample_accession': 'SAME123',
            'sample_ena_accession': 'ENA-SAMPLE-1'
        }
        run_experiment1 = {
            'run_experiment_accession': 'EXP123',
            'run_experiment_eva_accession': 'EVA1'
        }
        run_experiment2 = {
            'run_experiment_ena_accession': 'EXP456',
            'run_experiment_eva_accession': 'EVA2'
        }
        study_entity1 = ExcelLoader.map_row_entity(submission, 1, 'study', study)
        sample_entity1 = ExcelLoader.map_row_entity(submission, 1, 'sample', sample)
        run_entity1 = ExcelLoader.map_row_entity(submission, 1, 'run_experiment', run_experiment1)

        study_entity2 = ExcelLoader.map_row_entity(submission, 2, 'study', study)
        sample_entity2 = ExcelLoader.map_row_entity(submission, 2, 'sample', sample)
        run_entity2 = ExcelLoader.map_row_entity(submission, 2, 'run_experiment', run_experiment2)

        self.assertEqual(study_entity1, study_entity2)
        self.assertEqual(sample_entity1, sample_entity2)
        self.assertNotEqual(run_entity1, run_entity2)
        
        self.assertDictEqual(expected_accessions, submission.get_all_accessions())
        self.assertEqual('PRJEB12345', study_entity1.identifier.index)
        self.assertEqual('PRJEB12345', study_entity1.get_accession('BioStudies'))
        self.assertEqual('ENA-PROJECT-1', study_entity1.get_accession('ENA'))

        self.assertEqual('SAME123', sample_entity1.identifier.index)
        self.assertEqual('SAME123', sample_entity1.get_accession('BioSamples'))
        self.assertEqual('ENA-SAMPLE-1', sample_entity1.get_accession('ENA'))

        self.assertEqual('EXP123', run_entity1.identifier.index)
        self.assertEqual('EXP123', run_entity1.get_accession('ENA'))
        self.assertEqual('EVA1', run_entity1.get_accession('eva'))

        # only accessions in the format {entity_type}_accession can be used for indexes
        self.assertEqual('run_experiment:2', run_entity2.identifier.index)
        self.assertEqual('EXP456', run_entity2.get_accession('ENA'))
        self.assertEqual('EVA2', run_entity2.get_accession('eva'))
