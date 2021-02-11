from lxml import etree
from xml.etree.ElementTree import Element

from submission.submission import Submission
from .project import EnaProjectConverter
from .study import EnaStudyConverter
from .sample import EnaSampleConverter
from .experiment import EnaExperimentConverter
from .run import EnaRunConverter


class EnaSubmissionConverter:
    def __init__(self):
        self.conversions = {
            'projects.xml': self.projects_file,
            'studies.xml': self.studies_file,
            'samples.xml': self.samples_file,
            'experiments.xml': self.experiments_file,
            'runs.xml': self.runs_file,
            #  'submission.xml': self.submission_file
        }

    def convert(self, data: Submission) -> dict:
        ena_files = {}
        for file_name, converter in self.conversions.items():
            ena_files[file_name] = converter(data)
        return ena_files

    @staticmethod
    def projects_file(data: Submission) -> Element:
        project_converter = EnaProjectConverter()
        projects_node = etree.XML('<PROJECT_SET />')
        for study in data.get_entities('study'):
            projects_node.append(project_converter.convert(study))
        # Handle study.release_date
        return projects_node

    @staticmethod
    def studies_file(data: Submission) -> Element:
        study_converter = EnaStudyConverter()
        studies_node = etree.XML('<STUDY_SET />')
        for study in data.get_entities('study'):
            studies_node.append(study_converter.convert(study))
        # Handle study.release_date
        return studies_node

    @staticmethod
    def samples_file(data: Submission) -> Element:
        sample_converter = EnaSampleConverter()
        samples_node = etree.XML('<SAMPLE_SET />')
        for sample in data.get_entities('sample'):
            samples_node.append(sample_converter.convert(sample))
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
                    experiment.add_error('experiment_accession', 'No Linked Sample')
                if len(studies) < 1:
                    experiment.add_error('experiment_accession', 'No Linked Study')
            else:
                # ENA Only supports linking one study & sample to an experiment
                if len(samples) > 1:
                    experiment.add_error(f'More than one Sample Linked, using first: {samples[0].identifier.index}')
                if len(studies) > 1:
                    experiment.add_error(f'More than one Study Linked, using first: {studies[0].identifier.index}')
                experiments_node.append(experiment_converter.convert_experiment(experiment, samples[0], studies[0]))
        return experiments_node

    @staticmethod
    def runs_file(data: Submission) -> Element:
        run_converter = EnaRunConverter()
        runs_node = etree.XML('<RUN_SET />')
        for run in data.get_entities('run_experiment'):
            runs_node.append(run_converter.convert_run(run, experiment=run))
        return runs_node
