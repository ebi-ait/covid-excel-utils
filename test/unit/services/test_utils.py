import unittest
from unittest.mock import MagicMock

from excel.submission import ExcelSubmission
from services.utils import get_all_accessions_map
from submission.entity import Entity


class TestServiceUtils(unittest.TestCase):

    def setUp(self) -> None:
        self.__setup_mock_entities()

    def test_when_entities_has_accessions_returns_them_by_type(self):
        expected_accession_by_type = {
            'sample': ['SAME123', 'SAME456', 'SAME789'],
            'study': [self.bio_study_entity.get_accession()],
            'run_experiment': ['EXP123']
        }
        full_submission = ExcelSubmission()
        full_submission.get_entity_types = MagicMock(return_value=[
            'sample', 'study', 'run_experiment'
        ])
        full_submission.map_entity(self.bio_study_entity)
        full_submission.map_entity(self.bio_sample1_entity)
        full_submission.map_entity(self.bio_sample2_entity)
        full_submission.map_entity(self.bio_sample3_entity)
        full_submission.map_entity(self.run_experiment_entity)

        actual_accessions_by_type = get_all_accessions_map(full_submission)

        self.assertEqual(expected_accession_by_type, actual_accessions_by_type)

    def __setup_mock_entities(self):
        self.bio_study_attributes = {
            "study_accession": "PRJEB12345",
            "study_alias": "SARS-CoV-2 genomes 123ABC alias",
            "email_address": "joe@example.com",
            "center_name": "EBI",
            'study_name': 'SARS-CoV-2 genomes 123ABC name',
            "short_description": "test short description",
            "abstract": "test abstract",
            "release_date": "2020-08-21"
        }
        self.bio_study_entity = Entity(entity_type="study",
                                       index=self.bio_study_attributes["study_alias"],
                                       accession="BST123",
                                       attributes=self.bio_study_attributes)

        self.bio_sample1_attributes = {
            "sample_accession": "SAME123",
            "sample_alias": "sample1",
            "release_date": "2020-08-21"
        }
        self.bio_sample1_entity = Entity(entity_type="sample",
                                         index=self.bio_sample1_attributes["sample_alias"],
                                         accession=self.bio_sample1_attributes["sample_accession"],
                                         attributes=self.bio_sample1_attributes)
        self.bio_sample2_attributes = {
            "sample_accession": "SAME456",
            "sample_alias": "sample2",
            "release_date": "2020-08-21"
        }
        self.bio_sample2_entity = Entity(entity_type="sample",
                                         index=self.bio_sample2_attributes["sample_alias"],
                                         accession=self.bio_sample2_attributes["sample_accession"],
                                         attributes=self.bio_sample2_attributes)
        self.bio_sample3_attributes = {
            "sample_accession": "SAME789",
            "sample_alias": "sample3",
            "release_date": "2020-08-21"
        }
        self.bio_sample3_entity = Entity(entity_type="sample",
                                         index=self.bio_sample3_attributes["sample_alias"],
                                         accession=self.bio_sample3_attributes["sample_accession"],
                                         attributes=self.bio_sample3_attributes)

        self.run_experiment_attributes = {
            "experiment_accession": "EXP123",
            "experiment_alias": "exp1",
            "release_date": "2020-08-21"
        }
        self.run_experiment_entity = Entity(entity_type="run_experiment",
                                            index=self.run_experiment_attributes["experiment_alias"],
                                            accession=self.run_experiment_attributes["experiment_accession"],
                                            attributes=self.run_experiment_attributes)


if __name__ == '__main__':
    unittest.main()
