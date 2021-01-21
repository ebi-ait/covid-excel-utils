from lxml import etree
from .project import EnaProjectConverter


class EnaSubmission():
    projects = {}
    samples = {}
    experiments = {}
    runs = {}

    def files(self) -> dict:
        return {
            'projects.xml': self.projects_file(),
            # 'samples.xml': '',
            # 'experiments.xml': '',
            # 'runs.xml': ''
        }
    
    def projects_file(self):
        project_set = etree.XML('<PROJECT_SET />')
        for project in self.projects.values():
            project_set.append(project)
        return project_set


class EnaSubmissionConverter():
    def __init__(self):
        self.project_converter = EnaProjectConverter()

    def convert(self, data: dict) -> EnaSubmission:
        submission = EnaSubmission()
        for row_index, row in data.items():
            if 'study' in row:
                submission.projects[row_index] = self.project_converter.convert(row['study'])
                # ToDo: Handle study.release_date
        return submission
