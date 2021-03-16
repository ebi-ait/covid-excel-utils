import logging
import time

import docker
from .json import JsonValidator


class DockerValidator(JsonValidator):
    def __init__(self, image_name, validator_url, port=3020):
        self.__client = docker.from_env()
        self.container = self.__launch(self.__client, image_name, port)
        super().__init__(validator_url)
    
    def close(self):
        self.container.reload()
        if self.container:
            logging.debug(f'Stop running container: {self.container.name}')
            self.container.stop()
            logging.info(f'Removing container: {self.container.name}')
            self.container.remove()
            self.__client.close()
    
    @staticmethod
    def __launch(docker_client, image_name, port):
        if not docker_client.images.list(image_name):
            logging.info(f'Pulling image: {image_name}')
            docker_client.images.pull(image_name)
            logging.debug(f'Pulled image: {image_name}')
        containers = docker_client.containers.list(filters={'ancestor': image_name})
        if containers:
            logging.debug(f'Attaching to existing container from image: {image_name}')
            container = containers[0]
        else:
            logging.debug(f'Starting container from image: {image_name}')
            container = docker_client.containers.run(
                image_name,
                ports={f'{port}/tcp': port},
                detach=True
            )
            time.sleep(5)
        logging.info(f'Running Container: {container.name} from image: {image_name}')
        container.reload()
        return container
