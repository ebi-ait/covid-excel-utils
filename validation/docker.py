import logging
import time

import docker
from .schema import SchemaValidator


class DockerValidator(SchemaValidator):
    def __init__(self, image_name, validator_url, port=3020):
        self.__image_name = image_name
        self.__client = docker.from_env()
        self.__clean_up(self.__client, image_name)
        self.container = self.__launch(self.__client, image_name, port)
        super().__init__(validator_url)
    
    def close(self):
        if self.container:
            logging.info(f'Stop running {self.__image_name} container image.')
            self.container.stop()
            logging.info(f'Remove {self.__image_name} container image.')
            self.container.remove()
            self.__client.close()

    @staticmethod
    def __clean_up(docker_client, image_name):
        logging.info(f'Remove dangling container images with {image_name} name.')
        for state in ['created', 'restarting', 'removing', 'paused', 'exited', 'dead']:
            # This will remove the user's docker images, are we sure we want to do this?
            containers_to_remove = docker_client.containers.list(filters={'status': f'{state}'})
            for container_to_remove in containers_to_remove:
                container_to_remove.reload()
                container_to_remove.remove()
    
    @staticmethod
    def __launch(docker_client, image_name, port):
        if not docker_client.images.list(image_name):
            logging.info(f'Pull {image_name} container image from DockerHub.')
            docker_client.images.pull(image_name)
        containers = docker_client.containers.list(filters={'ancestor': image_name})
        if containers:
            container = containers[0].reload()
        else:
            logging.info(f'Run {image_name} container image locally.')
            container = docker_client.containers.run(
                image_name,
                ports={f'{port}/tcp': port},
                detach=True
            )
            time.sleep(5)
        return container
