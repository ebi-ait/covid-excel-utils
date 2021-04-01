from datetime import date
from typing import Dict, Tuple
from xml.etree.ElementTree import Element

from lxml import etree

from submission_broker.submission.entity import Entity
from submission_broker.submission.submission import Submission

from .project import EnaProjectConverter
from .study import EnaStudyConverter
from .sample import EnaSampleConverter
from .experiment import EnaExperimentConverter
from .run import EnaRunConverter

CONVERSION_MAP = [
    ('study', EnaProjectConverter()),
    ('study', EnaStudyConverter()),
    ('sample', EnaSampleConverter()),
    ('run_experiment', EnaExperimentConverter()),
    ('run_experiment', EnaRunConverter()),
]


class EnaSubmissionConverter:
    def get_ena_files(self, data: Submission) -> Dict[str, Tuple[str, str]]:
        ena_files = {}
        for entity_type, converter in CONVERSION_MAP:
            ena_type = converter.ena_type.upper()
            ena_set = etree.XML(f'<{ena_type}_SET />')
            for entity in data.get_entities(entity_type):
                ena_conversion = self.convert_entity(converter, data, entity)
                ena_set.append(ena_conversion)

            if len(ena_set) > 0:
                ena_files[ena_type] = (f'{ena_type}.xml', self.make_ena_file(ena_set))
        return ena_files

    @staticmethod
    def convert_entity(converter, data, entity):
        if isinstance(converter, EnaExperimentConverter):
            ena_conversion = EnaSubmissionConverter.convert_experiment(converter, data, entity)
        else:
            ena_conversion = converter.convert(entity)
        return ena_conversion

    @staticmethod
    def make_ena_file(element: Element) -> str:
        return etree.tostring(element, xml_declaration=True, pretty_print=True, encoding="UTF-8")

    @staticmethod
    def convert_experiment(converter: EnaExperimentConverter, data: Submission, experiment: Entity) -> Element:
        samples = data.get_linked_entities(experiment, 'sample')
        studies = data.get_linked_entities(experiment, 'study')

        if len(samples) < 1 or len(studies) < 1:
            if len(samples) < 1:
                experiment.add_error('run_experiment_ena_experiment_accession', 'No Linked Sample')
            if len(studies) < 1:
                experiment.add_error('run_experiment_ena_experiment_accession', 'No Linked Study')
        else:
            # ENA Only supports linking one study & sample to an experiment
            if len(samples) > 1:
                experiment.add_error('run_experiment_ena_experiment_accession', f'More than one Sample Linked, using first: {samples[0].identifier.index}')
            if len(studies) > 1:
                experiment.add_error('run_experiment_ena_experiment_accession', f'More than one Study Linked, using first: {studies[0].identifier.index}')
            sample = samples.pop()
            study = studies.pop()
            return converter.convert_experiment(experiment, sample, study)

    @staticmethod
    def get_release_date(data: Submission) -> date:
        if 'study' in data.get_entity_types():
            for study in data.get_entities('study'):
                if 'release_date' in study.attributes:
                    release_date = date.fromisoformat(study.attributes['release_date'])
                    if release_date > date.today():
                        return release_date
