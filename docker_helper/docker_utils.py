import sys
import time
import logging

import docker
from docker import errors
from requests.exceptions import ChunkedEncodingError


class DockerUtils:
    def __init__(self, image_name, port):
        self.client = docker.from_env()
        self.image_name = image_name
        self.port = port
        self.container = None

    def launch(self):
        if not self.client.images.list(self.image_name):
            self.client.images.pull(self.image_name)
        containers = self.client.containers.list(filters={'ancestor': self.image_name})
        if containers:
            self.container = containers[0]
        else:
            self.container = self.client.containers.run(
                self.image_name,
                ports={f'{self.port}/tcp': self.port},
                detach=True
            )
            time.sleep(5)

    def stop(self):
        logging.info(f'Stop running {self.image_name} container image.')
        self.container.stop()
        self.prune()

    def prune(self):
        logging.info('Prune all stopped container image.')
        self.client.containers.prune(filters={'ancestor': self.image_name})
