from enum import Enum

from submission.entity import Entity, EntityIdentifier

EXAMPLE__MAP = {
    'sample': {
        'hCoV-19/Ireland/D-NVRL-20G44567/2020': 'Entity',
        'hCoV-19/Ireland/D-NVRL-20G44568/2020': 'Entity'
    },
    'study': {
        'ICSC-Helixworks': 'Entity'
    },
    'entity_type': {
        'index': 'Entity'
    }
}


class HandleCollision(Enum):
    UPDATE = 1
    OVERWRITE = 2
    ERROR = 3


class Submission:
    __map = {}  # Upgrade python to 3.9 for dict[str, dict[str, Entity]]

    def __init__(self, collider: HandleCollision = None):
        self.collider = collider if collider else HandleCollision.UPDATE

    def __len__(self):
        count = 0
        for indexed_entities in self.__map.values():
            count = count + len(indexed_entities.values())

    def map(self, entity_type: str, index: str, accession: str, attributes: dict) -> Entity:
        entity = Entity(entity_type, index, accession, attributes)
        self.map_entity(entity)
        return entity

    def map_entity(self, entity: Entity):
        if self.__is_collision(entity.identifier):
            self.__handle_collision(entity)
        else:
            self.__map.setdefault(entity.identifier.entity_type, {})[entity.identifier.index] = entity

    def get_entities(self, entity_type: str):
        return self.__map[entity_type].values()

    def get_entity(self, entity_type: str, index: str) -> Entity:
        return self.__map[entity_type][index]

    def __is_collision(self, identifier: EntityIdentifier) -> bool:
        return identifier.entity_type in self.__map and identifier.index in self.__map[identifier.entity_type]

    def __handle_collision(self, entity: Entity):
        if self.collider == HandleCollision.ERROR:
            raise IndexError(f'Index {entity.identifier.index} already exists.')
        elif self.collider == HandleCollision.OVERWRITE:
            self.__map[entity.identifier.entity_type][entity.identifier.index] = entity
        else:  # Default is UPDATE
            existing_entity: Entity = self.__map[entity.identifier.entity_type][entity.identifier.index]
            existing_entity.attributes.update(entity.attributes)

    @staticmethod
    def link_entities(entity_a: Entity, entity_b: Entity):
        entity_a.links.add(entity_b.identifier)
        entity_b.links.add(entity_a.identifier)
