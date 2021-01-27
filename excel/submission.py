from submission.entity import Entity, EntityIdentifier
from submission.submission import Submission

EXAMPLE__ROW_ENTITIES = {
    '10': {
        'sample': 'hCoV-19/Ireland/D-NVRL-20G44567/2020',
        'study': 'ICSC-Helixworks'
    },
    '11': {
        'sample': 'hCoV-19/Ireland/D-NVRL-20G44568/2020',
        'study': 'ICSC-Helixworks'
    },
    'row': {
        'entity_type': 'index'
    }
}
EXAMPLE__ENTITY_ROWS = {
    'sample': {
        'hCoV-19/Ireland/D-NVRL-20G44567/2020': ['10'],
        'hCoV-19/Ireland/D-NVRL-20G44568/2020': ['11'],
    },
    'study': {
        'ICSC-Helixworks': ['10','11']
    },
    'entity_type': {
        'index': ['row'],
        'another_index': ['row1', 'row2'],
    }
}


class ExcelSubmission(Submission):
    __row_entities = {}
    __entity_rows = {}

    def map_row_entity(self, row: int, entity: Entity):
        super().map_entity(entity)
        self.__map_row(row, entity.identifier)
        self.__add_entity_links(row, entity)

    def __map_row(self, row: int, identifier: EntityIdentifier):
        self.__row_entities.setdefault(row, {})[identifier.entity_type] = identifier.index
        self.__entity_rows.setdefault(identifier.entity_type, {}).setdefault(identifier.index, []).append(row)

    def __add_entity_links(self, row: int, entity: Entity):
        for entity_type, index in self.__row_entities[row]:
            if entity_type != entity.identifier.entity_type:
                other_entity = self.get_entity(entity_type, index)
                self.link_entities(entity, other_entity)
