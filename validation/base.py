import logging

from submission_broker.submission.entity import Entity
from submission_broker.submission.submission import Submission


class BaseValidator:
    def validate_data(self, data: Submission):
        for entity_type, entities in data.get_all_entities().items():
            logging.info(f'Validating {len(entities)} {entity_type}(s) with {self.__class__}')
            for entity in entities:
                self.validate_entity(entity)

    def validate_entity(self, entity: Entity):
        # identify which attribute cases the error
        attribute = 'fake_attribute'
        error_msg = 'Example error message'
        entity.add_error(attribute, error_msg)
        # or if multiple errors occur for the same attribute
        error_msgs = ['error 1', 'error 2']
        entity.add_errors(attribute, error_msgs)
        raise NotImplementedError('Example validate entity used')
