from datetime import date
from lxml import etree
from xml.etree.ElementTree import Element

from submission.entity import Entity
from submission.submission import Submission
from .project import EnaProjectConverter
from .study import EnaStudyConverter
from .sample import EnaSampleConverter
from .experiment import EnaExperimentConverter
from .run import EnaRunConverter


class EnaSubmissionConverter:
    def __init__(self):
        self.conversions = {
            'PROJECT': self.projects_file,
            'STUDY': self.studies_file,
            'SAMPLE': self.samples_file,
            'EXPERIMENT': self.experiments_file,
            'RUN': self.runs_file,
            'SUBMISSION': self.submission_file
        }

    def convert(self, data: Submission) -> dict:
        ena_files = {}
        for file_name, converter in self.conversions.items():
            file_node = converter(data)
            if file_node:
                ena_files[file_name] = file_node
        return ena_files

    @staticmethod
    def projects_file(data: Submission) -> Element:
        project_converter = EnaProjectConverter()
        projects_node = etree.XML('<PROJECT_SET />')
        for study in data.get_entities('study'):
            projects_node.append(project_converter.convert(study))
        if len(projects_node):
            return projects_node

    @staticmethod
    def studies_file(data: Submission) -> Element:
        study_converter = EnaStudyConverter()
        studies_node = etree.XML('<STUDY_SET />')
        for study in data.get_entities('study'):
            studies_node.append(study_converter.convert(study))
        if len(studies_node):
            return studies_node

    @staticmethod
    def samples_file(data: Submission) -> Element:
        sample_converter = EnaSampleConverter()
        samples_node = etree.XML('<SAMPLE_SET />')
        for sample in data.get_entities('sample'):
            if not sample.get_accession('BioSamples'):
                samples_node.append(sample_converter.convert(sample))
        if len(samples_node):
            return samples_node

    @staticmethod
    def experiments_file(data: Submission) -> Element:
        experiment_converter = EnaExperimentConverter()
        experiments_node = etree.XML('<EXPERIMENT_SET />')
        for experiment in data.get_entities('run_experiment'):
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
                experiments_node.append(experiment_converter.convert_experiment(experiment, samples[0], studies[0]))
        if len(experiments_node):
            return experiments_node

    @staticmethod
    def runs_file(data: Submission) -> Element:
        run_converter = EnaRunConverter()
        runs_node = etree.XML('<RUN_SET />')
        for run in data.get_entities('run_experiment'):
            runs_node.append(run_converter.convert_run(run, experiment=run))
        if len(runs_node):
            return runs_node
    
    @staticmethod
    def submission_file(data: Submission) -> Element:
        submission = etree.Element('SUBMISSION')
        actions = etree.SubElement(submission, 'ACTIONS')
        action_add = etree.SubElement(actions, 'ACTION')
        etree.SubElement(action_add, 'ADD')
        if 'study' in data.get_entity_types():
            release_dates = set()
            study: Entity
            for study in data.get_entities('study'):
                if 'release_date' in study.attributes:
                    release_date = date.fromisoformat(study.attributes['release_date'])
                    if release_date > date.today():
                        release_dates.add(release_date)
            if len(release_dates) > 0:
                # Use first study release date, possible that file includes many 
                release_date = release_dates.pop()
                action_hold = etree.SubElement(actions, 'ACTION')
                hold = etree.SubElement(action_hold, 'HOLD')
                hold.attrib['HoldUntilDate'] = release_date.isoformat()
        return submission
