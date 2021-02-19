from enum import Enum
from typing import List

from submission.entity import Entity


class HandleCollision(Enum):
    UPDATE = 1
    OVERWRITE = 2
    ERROR = 3


class Submission:
    def __init__(self, collider: HandleCollision = None):
        self.__collider = collider if collider else HandleCollision.UPDATE
        self.__map = {}  # ToDo: Upgrade python to 3.9 for dict[str, dict[str, Entity]]

    def __len__(self):
        count = 0
        for indexed_entities in self.__map.values():
            count = count + len(indexed_entities.values())

    def map(self, entity_type: str, index: str, accession: str, attributes: dict) -> Entity:
        if entity_type in self.__map and index in self.__map[entity_type]:
            entity = self.__handle_collision(entity_type, index, attributes)
        else:
            entity = Entity(entity_type, index, accession, attributes)
            self.__map.setdefault(entity_type, {})[index] = entity
        return entity

    def get_entity_types(self):
        return self.__map.keys()

    def get_entities(self, entity_type: str):
        return self.__map[entity_type].values()

    def get_entity(self, entity_type: str, index: str) -> Entity:
        return self.__map[entity_type][index]
    
    def get_linked_entities(self, entity: Entity, entity_type: str) -> List[Entity]:
        entities = []
        for index in entity.get_linked_indexes(entity_type):
            entities.append(self.get_entity(entity_type, index))
        return entities

    def has_data(self) -> bool:
        for entities in self.__map.values():
            if len(entities.values()) > 0:
                return True
        return False
    
    def get_all_data(self) -> dict:
        data = {}
        for entity_type, indexed_entities in self.__map.items():
            for entity in indexed_entities.values():
                data[entity_type] = entity
        return data

    def has_errors(self) -> bool:
        for entities in self.__map.values():
            for entity in entities.values():
                if entity.errors:
                    return True
        return False

    def get_all_errors(self) -> dict:
        errors = {}
        for entity_type in self.get_entity_types():
            type_errors = self.get_type_errors(entity_type)
            if type_errors:
                errors[entity_type] = type_errors
        return errors
    
    def get_type_errors(self, entity_type: str):
        type_errors = {}
        for index, entity in self.__map[entity_type].items():
            if entity.errors:
                type_errors[index] = entity.errors
        return type_errors

    def __handle_collision(self, entity_type: str, index: str, attributes: dict) -> Entity:
        if self.__collider == HandleCollision.ERROR:
            raise IndexError(f'Index {index} already exists.')
        existing_entity: Entity = self.__map[entity_type][index]
        if self.__collider == HandleCollision.OVERWRITE:
            existing_entity.attributes = attributes
        else:  # Default is UPDATE
            existing_entity.attributes.update(attributes)
        return existing_entity

    @staticmethod
    def link_entities(entity_a: Entity, entity_b: Entity):
        entity_a.add_link_id(entity_b.identifier)
        entity_b.add_link_id(entity_a.identifier)
