from .base import BaseEnaConverter


TEMPLATE_FILE_PATH = 'conversion/ena/template/project.xml'
XPATH_SPEC = {
    '/PROJECT': {
        'accession': ['study_accession'],
        'alias': ['study_alias'],
        'center_name': ['center_name'],
    },
    '/PROJECT/NAME': ['study_name'],
    '/PROJECT/TITLE': ['short_description'],
    '/PROJECT/DESCRIPTION': ['abstract'],
}


class EnaProjectConverter(BaseEnaConverter):
    def __init__(self):
        super().__init__(TEMPLATE_FILE_PATH, XPATH_SPEC)
