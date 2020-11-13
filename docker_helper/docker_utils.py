import time
import logging

import docker

DOCKER_CONTAINER_STARTUP_TIME_IN_SECONDS = 5
NOT_RUNNING_CONTAINER_STATES = ['created', 'restarting', 'removing', 'paused', 'exited', 'dead']


class DockerUtils:
    def __init__(self, image_name, port):
        self.client = docker.from_env()
        self.image_name = image_name
        self.port = port
        self.container = None

    def launch(self):
        self.clean_up()
        if not self.client.images.list(self.image_name):
            logging.info(f'Pull {self.image_name} container image from DockerHub.')
            self.client.images.pull(self.image_name)
        containers = self.client.containers.list(filters={'ancestor': self.image_name})
        if containers:
            self.container = containers[0].reload()
        else:
            logging.info(f'Run {self.image_name} container image locally.')
            self.container = self.client.containers.run(
                self.image_name,
                ports={f'{self.port}/tcp': self.port},
                detach=True
            )
            time.sleep(DOCKER_CONTAINER_STARTUP_TIME_IN_SECONDS)

    def stop(self):
        logging.info(f'Stop running {self.image_name} container image.')
        self.container.stop()
        logging.info(f'Remove {self.image_name} container image.')
        self.container.remove()
        self.client.close()

    def clean_up(self):
        logging.info(f'Remove dangling container images with {self.image_name} name.')
        for state in NOT_RUNNING_CONTAINER_STATES:
            containers_to_remove = self.client.containers.list(filters={'status': f'{state}'})
            for container_to_remove in containers_to_remove:
                container_to_remove.reload()
                container_to_remove.remove()
