from submission.entity import Entity
from submission.submission import Submission


class BaseValidator:
    def validate_data(self, data: Submission):
        for entity_type in data.get_entity_types():
            for entity in data.get_entities(entity_type):
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
