from typing import Dict, List, Set

from submission_broker.submission.entity import Entity, EntityIdentifier
from submission_broker.submission.submission import Submission, HandleCollision


class ExcelSubmission(Submission):
    def __init__(self, collider: HandleCollision = None):
        super().__init__(collider)
        self.__entity_rows: Dict[str, Dict[str, Set[int]]] = {}
        self.__row_entities: Dict[int, Dict[str, str]] = {}

    def map(self, entity_type: str, index: str, attributes: dict) -> Entity:
        raise NotImplementedError('Use map_row instead to associate entity with excel row number.')

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
    
    def get_row_entities(self, row_index: int) -> Set[Entity]:
        entities = set()
        for entity_type, index in self.__row_entities[row_index].items():
            entities.add(super().get_entity(entity_type, index))
        return entities
    
    def get_row_errors(self, row_index: int) -> Dict[str, Dict[str, List[str]]]:
        row_errors = {}
        for entity in self.get_row_entities(row_index):
            if entity.has_errors():
                row_errors[entity.identifier.entity_type] = entity.get_errors()
        return row_errors

    def as_dict(self, string_lists: bool = False) -> Dict[str, Dict[str, dict]]:
        view = super().as_dict(string_lists)
        for entity_type, indexed_entities in view.items():
            for index, entity_dict in indexed_entities.items():
                if string_lists:
                    entity_dict['rows'] = str(list(self.get_rows(entity_type, index)))
                else:
                    entity_dict['rows'] = list(self.get_rows(entity_type, index))
        return view

    def get_all_errors(self) -> Dict[str, Dict[str, Dict[str, List[str]]]]:
        errors: Dict[str, Dict[str, Dict[str, List[str]]]] = {}
        for entity_type, entities in super().get_all_errors().items():
            for index, entity_errors in entities.items():
                row_index = f'rows:{list(self.get_rows(entity_type, index))}'
                errors.setdefault(entity_type, {})[row_index] = entity_errors
        return errors

    def __map_row_ids(self, row: int, identifier: EntityIdentifier):
        self.__row_entities.setdefault(row, {})[identifier.entity_type] = identifier.index
        self.__entity_rows.setdefault(identifier.entity_type, {}).setdefault(identifier.index, set()).add(row)

    def __add_entity_links(self, row: int, entity: Entity):
        for entity_type, index in self.__row_entities[row].items():
            if entity_type != entity.identifier.entity_type:
                other_entity = self.get_entity(entity_type, index)
                self.link_entities(entity, other_entity)
