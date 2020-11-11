import sys
import time
import logging

import docker
from docker import errors

from requests.exceptions import ChunkedEncodingError

RUNNING_STATE = 'running'


class DockerUtils:

    def __init__(self, dockerhub_url):
        self.dockerhub_url = dockerhub_url
        self.client = docker.from_env()

    def launch(self, image_name, port):
        try:
            self.image_exists_locally(image_name)
            container_name = self.create_container_name(image_name)
            if not(self.is_container_running(container_name)):
                self.run(image_name, container_name, port)
        except docker.errors.ImageNotFound:
            self.pull(image_name)
            self.launch(image_name, port)
        except ChunkedEncodingError:
            self.report_non_existing_container(image_name)

    def pull(self, image_name):
        try:
            logging.info(f'Pull {image_name} container image from DockerHub.')
            self.client.images.pull(image_name)
        except docker.errors.ImageNotFound:
            self.report_non_existing_container()

    def image_exists_locally(self, image_name):
        logging.info(f'Check whether {image_name} container image exists locally.')
        self.client.images.get(image_name)

    def is_container_running(self, name):
        logging.info(f'Check whether {name} container running locally.')
        containers = self.client.containers.list(all=True)
        if len(containers) == 0:
            return False

        container = self.client.containers.get(name)
        status = container.status

        if status != RUNNING_STATE:
            self.client.containers.prune()
            return False

        return True

    def run(self, image_name, container_name, port=3020):
        logging.info(f'{image_name} container image is not running. Will try to run it now ...')
        self.client.containers.run(image_name, ports={f'{port}/tcp': port},
                                   name=container_name, detach=True)
        time.sleep(2)

    def stop(self, image_name):
        logging.info(f'Stop running {image_name} container image.')
        container = self.client.containers.get(image_name)
        container.stop()

    def prune(self):
        logging.info('Prune all stopped container image.')
        self.client.containers.prune()

    @staticmethod
    def create_container_name(image_name):
        return str(image_name).replace('/', '__')

    @staticmethod
    def report_non_existing_container(self, image_name):
        logging.error(
            f'Docker container with name: {image_name} does not exist.')
        sys.exit(10)
