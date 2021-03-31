from typing import Dict, Tuple

from submission.entity import Entity
from submission.submission import Submission
from .sample import SAMPLE_ACCESSION_PRIORITY
from .experiment import EnaExperimentConverter
from .run import EnaRunConverter

SUBMISSION_TOOL = "drag and drop uploader tool"


class EnaManifestConverter:
    def __init__(self, schema:dict):
        self.platforms = schema.get('properties', {}).get('sequencing_platform', {}).get('enum', [])
        self.instruments = schema.get('properties', {}).get('sequencing_instrument', {}).get('enum', [])
        self.library_sources = schema.get('properties', {}).get('library_source', {}).get('enum', [])
        self.library_selections = schema.get('properties', {}).get('library_selection', {}).get('enum', [])
        self.library_strategies = schema.get('properties', {}).get('library_strategy', {}).get('enum', [])

    def make_manifests(self, submission: Submission) -> Dict[str, str]:
        manifests = {}
        for run_experiment in submission.get_entities('run_experiment'):
            samples = submission.get_linked_entities(run_experiment, 'sample')
            studies = submission.get_linked_entities(run_experiment, 'study')
            if len(samples) == 1 and len(studies) == 1 and 'uploaded_file_1' in run_experiment.attributes:
                sample = samples.pop()
                study = studies.pop()
                sample_accession = sample.get_first_accession(SAMPLE_ACCESSION_PRIORITY)
                study_accession = study.get_accession('ENA_Study')
                if sample_accession and study_accession:
                    file_name, content = self.make_manifest(run_experiment, sample_accession, study_accession)
                    manifests[file_name] = content
        return manifests

    def make_manifest(self, run_experiment: Entity, sample_accession: str, study_accession: str) -> Tuple[str, str]:
        manifest_lines = []
        manifest_lines.append(f'STUDY\t{study_accession}')
        manifest_lines.append(f'SAMPLE\t{sample_accession}')
        manifest_lines.append(f'NAME\t{run_experiment.identifier.index}')

        platform = self.valid_platform(run_experiment.attributes.get('sequencing_platform', ''))
        if platform:
            manifest_lines.append(f'PLATFORM\t{platform}')

        instrument = self.valid_instrument(run_experiment.attributes.get('sequencing_instrument', ''))
        manifest_lines.append(f'INSTRUMENT\t{instrument}')
        
        paired_fastq = EnaExperimentConverter.is_paired_fastq(run_experiment)
        if paired_fastq:
            manifest_lines.append(f"INSERT_SIZE\t{run_experiment.attributes['insert_size']}")
        
        library_name = run_experiment.attributes.get('library_name', '')
        if library_name:
            manifest_lines.append(f'LIBRARY_NAME\t{library_name}')
        
        library_source = self.valid_library_source(run_experiment.attributes.get('library_source', ''))
        manifest_lines.append(f'LIBRARY_SOURCE\t{library_source}')

        library_selection = self.valid_library_selection(run_experiment.attributes.get('library_selection', 'unspecified'))
        manifest_lines.append(f'LIBRARY_SELECTION\t{library_selection}')

        library_strategy = self.valid_library_strategy(run_experiment.attributes.get('library_strategy', ''))
        manifest_lines.append(f'LIBRARY_STRATEGY\t{library_strategy}')
        manifest_lines.append(f'SUBMISSION_TOOL\t{SUBMISSION_TOOL}')

        file_name = run_experiment.attributes['uploaded_file_1']
        file_type = EnaRunConverter.get_file_type(file_name).upper()
        manifest_lines.append(f'{file_type}\t{file_name}')
        if paired_fastq:
            paired_file = run_experiment.attributes['uploaded_file_2']
            file_name += f'.{paired_file}'
            manifest_lines.append(f'{file_type}\t{paired_file}')
        file_name += '.manifest'
        return file_name, '\n'.join(manifest_lines)

    def valid_platform(self, platform: str) -> str:
        converted_platform = platform.upper().replace(' ', '_')
        if converted_platform in self.platforms:
            return converted_platform

    def valid_instrument(self, instrument: str) -> str:
        if instrument in self.instruments:
            return instrument
        return 'unspecified'

    def valid_library_source(self, library_source: str) -> str:
        if library_source in self.library_sources:
            return library_source
        return 'OTHER'

    def valid_library_selection(self, library_selection: str) -> str:
        if library_selection in self.library_selections:
            return library_selection
        return 'other'
    
    def valid_library_strategy(self, library_strategy: str) -> str:
        if library_strategy in self.library_strategies:
            return library_strategy
        return 'OTHER'
