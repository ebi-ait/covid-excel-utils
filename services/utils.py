from excel.submission import ExcelSubmission


def get_all_accessions_map(full_submission: ExcelSubmission):
    accessions_by_type = {}
    entity_types = full_submission.get_entity_types()

    for entity_type in entity_types:
        accessions_by_type[entity_type] = []
        for entity in full_submission.get_entities(entity_type):
            accession = entity.get_accession()
            if accession:
                accessions_by_type[entity_type].append(accession)

    return accessions_by_type
