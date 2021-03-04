import unittest

from excel.load import ExcelLoader
from excel.submission import ExcelSubmission


class TestExcelAccessionHandling(unittest.TestCase):
    def test_default_accessions(self):
        expected_accessions = {
            'BioStudies': ['S-BSST1'],
            'BioSamples': ['SAME1'],
            'ENA_Run': ['ERR1', 'ERR2']
        }
        submission = ExcelSubmission()
        study = {
            'study_accession': 'S-BSST1',
        }
        sample = {
            'sample_accession': 'SAME1',
        }
        run_experiment1 = {
            'run_experiment_accession': 'ERR1',
        }
        run_experiment2 = {
            'run_experiment_accession': 'ERR2',
        }
        study_entity1 = ExcelLoader.map_row_entity(submission, 1, 'study', study)
        sample_entity1 = ExcelLoader.map_row_entity(submission, 1, 'sample', sample)
        run_entity1 = ExcelLoader.map_row_entity(submission, 1, 'run_experiment', run_experiment1)
        run_entity2 = ExcelLoader.map_row_entity(submission, 2, 'run_experiment', run_experiment2)
        
        self.assertDictEqual(expected_accessions, submission.get_all_accessions())
        self.assertEqual('S-BSST1', study_entity1.identifier.index)
        self.assertEqual('S-BSST1', study_entity1.get_accession('BioStudies'))

        self.assertEqual('SAME1', sample_entity1.identifier.index)
        self.assertEqual('SAME1', sample_entity1.get_accession('BioSamples'))

        self.assertEqual('ERR1', run_entity1.identifier.index)
        self.assertEqual('ERR1', run_entity1.get_accession('ENA_Run'))

        self.assertEqual('ERR2', run_entity2.identifier.index)
        self.assertEqual('ERR2', run_entity2.get_accession('ENA_Run'))
    
    def test_mapped_accessions(self):
        expected_accessions = {
            'BioStudies': ['S-BSST1'],
            'BioSamples': ['SAME1'],
            'ENA_Project': ['PRJEB1'],
            'ENA_Study': ['ERP1'],
            'ENA_Sample': ['ERS1'],
            'ENA_Experiment': ['ERX1', 'ERX2'],
            'ENA_Run': ['ERR1', 'ERR2']
        }
        submission = ExcelSubmission()
        study = {
            'study_biostudies_accession': 'S-BSST1',
            'study_ena_project_accession': 'PRJEB1',
            'study_ena_study_accession': 'ERP1'
        }
        sample = {
            'sample_biosamples_accession': 'SAME1',
            'sample_ena_sample_accession': 'ERS1'
        }
        run_experiment1 = {
            'run_experiment_ena_experiment_accession': 'ERX1',
            'run_experiment_ena_run_accession': 'ERR1',

        }
        run_experiment2 = {
            'run_experiment_ena_experiment_accession': 'ERX2',
            'run_experiment_ena_run_accession': 'ERR2',
        }
        study_entity1 = ExcelLoader.map_row_entity(submission, 1, 'study', study)
        sample_entity1 = ExcelLoader.map_row_entity(submission, 1, 'sample', sample)
        run_entity1 = ExcelLoader.map_row_entity(submission, 1, 'run_experiment', run_experiment1)
        run_entity2 = ExcelLoader.map_row_entity(submission, 2, 'run_experiment', run_experiment2)
        
        self.assertDictEqual(expected_accessions, submission.get_all_accessions())
        self.assertEqual('S-BSST1', study_entity1.get_accession('BioStudies'))
        self.assertEqual('PRJEB1', study_entity1.get_accession('ENA_Project'))
        self.assertEqual('ERP1', study_entity1.get_accession('ENA_Study'))

        self.assertEqual('SAME1', sample_entity1.get_accession('BioSamples'))
        self.assertEqual('ERS1', sample_entity1.get_accession('ENA_Sample'))

        self.assertEqual('ERR1', run_entity1.get_accession('ENA_Run'))
        self.assertEqual('ERX1', run_entity1.get_accession('ENA_Experiment'))

        self.assertEqual('ERR2', run_entity2.get_accession('ENA_Run'))
        self.assertEqual('ERX2', run_entity2.get_accession('ENA_Experiment'))

    def test_unmapped_service_accessions(self):
        expected_accessions = {
            'array_express': ['A1', 'A2'],
            'eva': ['EVA1', 'EVA2']
        }
        submission = ExcelSubmission()
        sequence1 = {
            'sequence_array_express_accession': 'A1',
            'sequence_eva_accession': 'EVA1',
        }
        sequence2 = {
            'sequence_array_express_accession': 'A2',
            'sequence_eva_accession': 'EVA2',
        }
        sequence_entity1 = ExcelLoader.map_row_entity(submission, 1, 'sequence', sequence1)
        sequence_entity2 = ExcelLoader.map_row_entity(submission, 2, 'sequence', sequence2)
        
        self.assertDictEqual(expected_accessions, submission.get_all_accessions())
        self.assertEqual('A1', sequence_entity1.get_accession('array_express'))
        self.assertEqual('EVA1', sequence_entity1.get_accession('eva'))
        self.assertEqual('A2', sequence_entity2.get_accession('array_express'))
        self.assertEqual('EVA2', sequence_entity2.get_accession('eva'))
        
    def test_umnapped_no_service_accession(self):
        # In the case that {object}_accession is used in the excel for an object that isn't configured with a default service
        # Use the accession as an index but do not add the accession to the entity.
        attributes = {
            'lorem_accession': 'ipsum'
        }

        submission = ExcelSubmission()
        lorem_entity = ExcelLoader.map_row_entity(submission, 1, 'lorem', attributes)

        self.assertEqual('ipsum', lorem_entity.identifier.index)
        self.assertDictEqual({}, lorem_entity.__accessions)
