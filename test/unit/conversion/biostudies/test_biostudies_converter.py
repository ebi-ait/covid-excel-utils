import unittest

from conversion.biostudies.bio_study_converter import BioStudyConverter
from submission.entity import Entity


class TestBioStudiesConverter(unittest.TestCase):

    def test_passed_bio_study_entity_returns_correct_json_representative(self):
        bio_study_attributes = {
            "study_accession": "PRJEB12345",
            "study_alias": "SARS-CoV-2 genomes 123ABC alias",
            "email_address": "joe@example.com",
            "center_name": "EBI",
            'study_name': 'SARS-CoV-2 genomes 123ABC name',
            "short_description": "test short description",
            "abstract": "test abstract",
            "release_date": "2020-08-21"
        }
        bio_study_entity = Entity(entity_type="study", index=bio_study_attributes["study_alias"],
                                  attributes=bio_study_attributes)

        expected_payload = self.__get_expected_payload(bio_study_entity)

        bio_study_json_payload = BioStudyConverter.convert_study(bio_study_entity)

        self.assertDictEqual(expected_payload, bio_study_json_payload)

    @staticmethod
    def __get_expected_payload(bio_study_entity):
        expected_payload = {
            "attributes": [
                {
                    "name": "Name",
                    "value": bio_study_entity.attributes["study_name"]
                },
                {
                    "name": "ReleaseDate",
                    "value": bio_study_entity.attributes["release_date"]
                }
            ],
            "section": {
                "accno": "PROJECT",
                "type": "Study",
                "attributes": [
                    {
                        "name": "Study alias",
                        "value": bio_study_entity.attributes["study_alias"]
                    },
                    {
                        "name": "Name",
                        "value": bio_study_entity.attributes["study_name"]
                    },
                    {
                        "name": "Title",
                        "value": bio_study_entity.attributes["short_description"]
                    },
                    {
                        "name": "Description",
                        "value": bio_study_entity.attributes["abstract"]
                    }
                ],
                "subsection": [
                    {
                        "type": "Author",
                        "attributes": [
                            {
                                "name": "Email address",
                                "value": bio_study_entity.attributes["email_address"]
                            },
                            {
                                "name": "Centre name",
                                "value": bio_study_entity.attributes["center_name"]
                            }
                        ]
                    }
                ]
            }
        }

        return expected_payload


if __name__ == '__main__':
    unittest.main()
