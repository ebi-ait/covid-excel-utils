from json_converter.json_mapper import JsonMapper

from conversion.conversion_utils import fixed_attribute
from submission.entity import Entity


BIO_STUDY_SPEC = {
    'attributes': ['$array', [
            {
                'name': ['', fixed_attribute, 'Name'],
                'value': ['study_name']
            },
            {
                'name': ['', fixed_attribute, 'Release Date'],
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
        'links': [
            '$array', [
                {
                    'url': ['study_accession'],
                    'attributes': [
                        '$array', [
                            {
                                'name': ['', fixed_attribute, 'Type'],
                                'value': ['', fixed_attribute, 'ENA']
                            }
                        ],
                        True
                    ]
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
    def convert(entity: Entity):

        return JsonMapper(entity.attributes).map(BIO_STUDY_SPEC)
