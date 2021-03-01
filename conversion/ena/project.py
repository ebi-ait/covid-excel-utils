from conversion.conversion_utils import fixed_attribute
from .base import BaseEnaConverter


PROJECT_SPEC = {
    '@center_name': ['center_name'],
    'NAME': ['study_name'],
    'TITLE': ['short_description'],
    'DESCRIPTION': ['abstract'],
    'SUBMISSION_PROJECT': {
        'SEQUENCING_PROJECT': ['', fixed_attribute, '']
    }
}


class EnaProjectConverter(BaseEnaConverter):
    def __init__(self):
        super().__init__(ena_type='Project', xml_spec=PROJECT_SPEC)
