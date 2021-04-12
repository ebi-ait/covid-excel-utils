import json
from os.path import dirname, join, splitext


def load_schema_files(schema_validator):
    current_folder = dirname(__file__)
    for file in ["schema/isolate_genome_assembly_information.json",
                 "schema/study.json",
                 "schema/sample.json",
                 "schema/run_experiment.json"]:
        with open(join(current_folder, file)) as schema_file:
            entity_type = splitext(file)[0].split('/')[-1]
            schema_validator.schema_by_type[entity_type] = json.load(schema_file)
