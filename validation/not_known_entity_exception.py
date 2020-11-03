class NotKnownEntityException(Exception):
    def __init__(self, entity_name):
        self.entity_name = entity_name

    def __str__(self):
        return f'The provided entity not known by the application: {self.entity_name}'