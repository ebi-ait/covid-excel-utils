from json_converter.json_mapper import JsonMapper
from typing import List

from conversion.conversion_utils import fixed_attribute
from submission.entity import Entity


BIO_STUDY_SPEC = {
    'attributes': ['$array', [
            {
                'name': ['', fixed_attribute, 'Name'],
                'value': ['study_name']
            },
            {
                'name': ['', fixed_attribute, 'ReleaseDate'],
                'value': ['release_date']
            }
        ],
        True
    ],
    'section': {
        'accno': ['', fixed_attribute, 'PROJECT'],
        'type': ['', fixed_attribute, 'Study'],
        'attributes': [
            '$array', [
                {
                    'name': ['', fixed_attribute, 'Study alias'],
                    'value': ['study_alias']
                },
                {
                    'name': ['', fixed_attribute, 'Name'],
                    'value': ['study_name']
                },
                {
                    'name': ['', fixed_attribute, 'Title'],
                    'value': ['short_description']
                },
                {
                    'name': ['', fixed_attribute, 'Description'],
                    'value': ['abstract']
                }
            ],
            True
        ],
        'subsection': [
            '$array', [
                {
                    'type': ['', fixed_attribute, 'Author'],
                    'attributes': [
                        '$array', [
                            {
                                'name': ['', fixed_attribute, 'Email address'],
                                'value': ['email_address']
                            },
                            {
                                'name': ['', fixed_attribute, 'Centre name'],
                                'value': ['center_name']
                            }
                        ],
                        True
                    ]
                }
            ],
            True
        ]
    }
}


class BioStudyConverter:

    @staticmethod
    def convert_all_studies(studies: List[Entity]):
        biostudies_submissions = []
        for study in studies:
            biostudies_submissions.append(BioStudyConverter.convert_study(study))

        return biostudies_submissions

    @staticmethod
    def convert_study(entity: Entity):

        return JsonMapper(entity.attributes).map(BIO_STUDY_SPEC)
