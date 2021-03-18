from copy import deepcopy
from typing import Dict, Iterable, ItemsView, Set, List


class EntityIdentifier:
    def __init__(self, entity_type: str, index: str):
        self.entity_type = entity_type  # examples: project, study, sample, experiment_run
        self.index = index  # example: hCoV-19/Ireland/D-NVRL-20G44567/2020

    def __hash__(self):
        return hash((self.entity_type, self.index))


class Entity:
    def __init__(self, entity_type: str, index: str, attributes: dict):
        self.identifier = EntityIdentifier(entity_type, index)
        self.attributes = attributes
        self.__accessions: Dict[str, str] = {}
        self.__errors: Dict[str, List[str]] = {}
        self.__links: Dict[str, Set[str]] = {}

    def add_error(self, attribute: str, error_msg: str):
        self.__errors.setdefault(attribute, []).append(error_msg)

    def add_errors(self, attribute: str, error_msgs: Iterable[str]):
        self.__errors.setdefault(attribute, []).extend(error_msgs)

    def get_errors(self) -> Dict[str, List[str]]:
        return deepcopy(self.__errors)

    def has_errors(self) -> bool:
        return len(self.__errors) > 0

    def add_link_id(self, identifier: EntityIdentifier):
        self.add_link(identifier.entity_type, identifier.index)

    def add_link(self, entity_type: str, index: str):
        self.__links.setdefault(entity_type, set()).add(index)

    def get_linked_indexes(self, entity_type) -> Set[str]:
        return self.__links.get(entity_type, set())

    def add_accession(self, service: str, accession_value: str):
        self.__accessions[service] = accession_value

    def get_accession(self, service: str) -> str:
        return self.__accessions.get(service, None)

    def get_first_accession(self, service_priority: Iterable[str]):
        for service in service_priority:
            accession = self.get_accession(service)
            if accession:
                return accession

    def get_accessions(self) -> ItemsView[str, str]:
        return self.__accessions.items()

    def as_dict(self, with_id: bool = False, string_lists: bool = False) -> dict:
        view = {}
        if with_id:
            view['id'] = f'{self.identifier.entity_type}:{self.identifier.index}'
        if self.attributes:
            view['attributes'] = deepcopy(self.attributes)
        if len(self.__accessions) > 0:
            view['accessions'] = deepcopy(self.__accessions)
        if len(self.__links) > 0:
            view['links'] = self.__links_as_dict(string_lists)
        if self.has_errors():
            view['errors'] = self.get_errors()
        return view

    def __links_as_dict(self, string_list: bool = False) -> dict:
        links = {}
        for entity_type, indexes in self.__links.items():
            if string_list:
                links[entity_type] = str(list(indexes))
            else:
                links[entity_type] = list(indexes)
        return links
