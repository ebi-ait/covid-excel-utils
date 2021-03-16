from typing import Dict, List, Set

from submission.entity import Entity, EntityIdentifier
from submission.submission import Submission, HandleCollision


class ExcelSubmission(Submission):
    def __init__(self, collider: HandleCollision = None):
        super().__init__(collider)
        self.__entity_rows: Dict[str, Dict[str, Set[int]]] = {}
        self.__row_entities: Dict[int, Dict[str, str]] = {}

    def map_row(self, row: int, entity_type: str, index: str, attributes: dict) -> Entity:
        entity = super().map(entity_type, index, attributes)
        self.__map_row_ids(row, entity.identifier)
        self.__add_entity_links(row, entity)
        return entity

    def get_rows_from_id(self, identifier: EntityIdentifier) -> Set[int]:
        return self.get_rows(identifier.entity_type, identifier.index)

    def get_rows(self, entity_type: str, index: str) -> Set[int]:
        return self.__entity_rows.get(entity_type, {}).get(index, set())
    
    def get_all_rows(self):
        return self.__row_entities.keys()

    def get_all_data(self) -> Dict[int, Dict[str, dict]]:
        data: Dict[int, Dict[str, dict]] = {}
        for entity_type, entities in self.get_all_entities().items():
            for entity in entities:
                for row in self.get_rows_from_id(entity.identifier):
                    data.setdefault(row, {})[entity_type] = entity.attributes
        return data

    def get_all_errors(self) -> Dict[int, Dict[str, Dict[str, List[str]]]]:
        errors: Dict[int, Dict[str, Dict[str, List[str]]]] = {}
        for entity_type, entities in super().get_all_errors().items():
            for index, entity_errors in entities.items():
                for row in self.get_rows(entity_type, index):
                    errors.setdefault(row, {})[entity_type] = entity_errors
        return errors

    def __map_row_ids(self, row: int, identifier: EntityIdentifier):
        self.__row_entities.setdefault(row, {})[identifier.entity_type] = identifier.index
        self.__entity_rows.setdefault(identifier.entity_type, {}).setdefault(identifier.index, set()).add(row)

    def __add_entity_links(self, row: int, entity: Entity):
        for entity_type, index in self.__row_entities[row].items():
            if entity_type != entity.identifier.entity_type:
                other_entity = self.get_entity(entity_type, index)
                self.link_entities(entity, other_entity)
