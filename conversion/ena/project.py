from .base import BaseEnaConverter


PROJECT_SPEC = {
    '@accession': ['study_accession'],
    '@alias': ['study_alias'],
    '@center_name': ['center_name'],
    'NAME': ['study_name'],
    'TITLE': ['short_description'],
    'DESCRIPTION': ['abstract'],
    'SUBMISSION_PROJECT': ['$object', {
        'SEQUENCING_PROJECT': {}
    }]  # $object keyword for JSON Literal
}


class EnaProjectConverter(BaseEnaConverter):
    def __init__(self):
        super().__init__(root_name='PROJECT', xml_spec=PROJECT_SPEC)
