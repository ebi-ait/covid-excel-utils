from .schema import SchemaValidator
from docker_helper.docker_utils import DockerUtils


class DockerValidator(SchemaValidator):
    def __init__(self, image_name, validator_url, port=3020):
        self.docker_utils = DockerUtils(image_name, port)
        super().__init__(validator_url)
    
    def close(self):
        self.docker_utils.stop()
