from conversion.ena.base import BaseEnaConverter
from datetime import date
from typing import Dict, List, Tuple
from xml.etree.ElementTree import Element

from lxml import etree

from submission_broker.submission.entity import Entity
from submission_broker.submission.submission import Submission

from .project import EnaProjectConverter
from .study import EnaStudyConverter
from .sample import EnaSampleConverter
from .experiment import EnaExperimentConverter
from .run import EnaRunConverter


class EnaSubmissionConverter:
    def __init__(self, target_objects: List[str] = None):
        if not target_objects:
            target_objects = ['ENA_Project', 'ENA_Sample', 'ENA_Experiment', 'ENA_Run']
        self.conversion_map = []
        if 'ENA_Project' in target_objects:
            self.conversion_map.append(('study', EnaProjectConverter()))
        elif 'ENA_Study' in target_objects:
            self.conversion_map.append(('study', EnaStudyConverter()))
        if 'ENA_Sample' in target_objects:
            self.conversion_map.append(('sample', EnaSampleConverter()))
        if 'ENA_Experiment' in target_objects:
            self.conversion_map.append(('run_experiment', EnaExperimentConverter()))
        if 'ENA_Run' in target_objects:
            self.conversion_map.append(('run_experiment', EnaRunConverter()))
        
    def get_ena_files(self, data: Submission) -> Dict[str, Tuple[str, str]]:
        ena_files = {}
        for entity_type, converter in self.conversion_map:
            ena_type = converter.ena_type.upper()
            ena_set = etree.XML(f'<{ena_type}_SET />')
            for entity in data.get_entities(entity_type):
                ena_conversion = self.convert_entity(converter, data, entity)
                ena_set.append(ena_conversion)

            if len(ena_set) > 0:
                ena_files[ena_type] = (f'{ena_type}.xml', self.make_ena_file(ena_set))
        return ena_files

    @staticmethod
    def convert_entity(converter: BaseEnaConverter, data, entity):
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
            len_samples = len(samples)
            len_studies = len(studies)
            sample = samples.pop()
            study = studies.pop()

            # ENA Only supports linking one study & sample to an experiment
            if len_samples > 1:
                experiment.add_error('run_experiment_ena_experiment_accession', f'More than one Sample Linked, using first: {sample.identifier.index}')
            if len_studies > 1:
                experiment.add_error('run_experiment_ena_experiment_accession', f'More than one Study Linked, using first: {study.identifier.index}')
            return converter.convert_experiment(experiment, sample, study)

    @staticmethod
    def get_release_date(data: Submission) -> date:
        if 'study' in data.get_entity_types():
            for study in data.get_entities('study'):
                if 'release_date' in study.attributes:
                    release_date = date.fromisoformat(study.attributes['release_date'])
                    if release_date > date.today():
                        return release_date
