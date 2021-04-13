import unittest

from submission_broker.submission.submission import Submission


class TestSubmissionAccessions(unittest.TestCase):

    def setUp(self) -> None:
        self.maxDiff = None
        self.__setup_mock_entities()

    def test_when_entities_has_accessions_returns_them_by_type(self):
        expected_accession_by_type = {
            'BioSamples': {'SAME123', 'SAME456', 'SAME789'},
            'BioStudies': {"BST1"},
            'ENA': {'EXP123'}
        }
        submission = Submission()

        study = submission.map("study", "study", self.study)
        study.add_accession('BioStudies', "BST1")

        sample1 = submission.map("sample", "sample1", self.sample1)
        sample1.add_accession('BioSamples', "SAME123")

        sample2 = submission.map("sample", "sample2", self.sample2)
        sample2.add_accession('BioSamples', "SAME456")

        sample3 = submission.map("sample", "sample3", self.sample3)
        sample3.add_accession('BioSamples', "SAME789")

        run_experiment = submission.map("run_experiment", "sample3", self.run_experiment)
        run_experiment.add_accession('ENA', "EXP123")

        self.assertEqual(expected_accession_by_type, submission.get_all_accessions())

    def __setup_mock_entities(self):
        self.study = {
            "study_accession": "PRJEB12345",
            "study_alias": "SARS-CoV-2 genomes 123ABC alias",
            "email_address": "joe@example.com",
            "center_name": "EBI",
            'study_name': 'SARS-CoV-2 genomes 123ABC name',
            "short_description": "test short description",
            "abstract": "test abstract",
            "release_date": "2020-08-21"
        }

        self.sample1 = {
            "sample_accession": "SAME123",
            "sample_alias": "sample1",
            "release_date": "2020-08-21"
        }

        self.sample2 = {
            "sample_accession": "SAME456",
            "sample_alias": "sample2",
            "release_date": "2020-08-21"
        }

        self.sample3 = {
            "sample_accession": "SAME789",
            "sample_alias": "sample3",
            "release_date": "2020-08-21"
        }

        self.run_experiment = {
            "experiment_accession": "EXP123",
            "experiment_alias": "exp1",
            "release_date": "2020-08-21"
        }


if __name__ == '__main__':
    unittest.main()
